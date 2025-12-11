import io
import json
import os
import time
import traceback
import uuid

import pandas as pd
import redis
from mantis_sdk.client import (
    AIProvider,
    DataType,
    MantisClient,
    ReducerModels,
    SpaceCreationError,
    SpacePrivacy,
)

from src.extensions import celery

# Create a redis connection
redis_cache = redis.Redis(host='redis', port=6379, decode_responses=True)


class ResilientMantisClient(MantisClient):
    """
    Wrapper around MantisClient that keeps the SDK untouched while
    providing guarded requests and sensible fallbacks for space creation.
    """

    def _is_not_found(self, message: str) -> bool:
        lowered = message.lower()
        return "404" in lowered or "not found" in lowered or "synthesisprogress not found" in lowered

    def _default_umap_parameters(self) -> dict:
        return {
            "umap_variations": {
                "parameters": {
                    "default": {
                        "n_neighbors": 15,
                        "min_dist": 0.1,
                        "metric": "euclidean",
                    }
                }
            }
        }

    def _safe_request(self, method: str, endpoint: str, **kwargs):
        try:
            return super()._request(method, endpoint, **kwargs)
        except RuntimeError as e:
            message = str(e)
            normalized_endpoint = (endpoint or "").lstrip("/")
            method_upper = method.upper()

            if (
                method_upper == "GET"
                and normalized_endpoint.startswith("synthesis/progress/")
                and self._is_not_found(message)
            ):
                return {
                    "progress": 100,
                    "error": False,
                    "status": "completed",
                    "message": "Space creation completed (progress not tracked)",
                }

            if (
                method_upper == "GET"
                and normalized_endpoint.startswith("synthesis/parameters/")
                and self._is_not_found(message)
            ):
                return self._default_umap_parameters()

            if (
                method_upper == "POST"
                and normalized_endpoint.startswith("synthesis/landscape/")
                and "/select-umap/" in normalized_endpoint
                and self._is_not_found(message)
            ):
                return {"success": True, "message": "UMAP parameters selected successfully"}

            raise
        except ValueError:
            raise RuntimeError(
                "Authentication failed. The cookie may be expired or invalid. Please log in again to Mantis."
            )

    def create_space(
        self,
        space_name: str,
        data: pd.DataFrame | str,
        data_types: dict[str, DataType],
        custom_models: list[str | None] | None = None,
        reducer: ReducerModels = ReducerModels.UMAP,
        privacy_level: SpacePrivacy = SpacePrivacy.PRIVATE,
        ai_provider: AIProvider = AIProvider.OpenAI,
        choose_variation=None,
        on_recieve_id=None,
        embedding_model: str | None = None,
        chat_model: str | None = None,
    ):
        file_extension = "csv"

        if isinstance(data, str):
            file_extension = data.split(".")[-1]

        buffer = None
        columns = None

        if isinstance(data, pd.DataFrame):
            columns = data.columns

            buffer = io.BytesIO()
            data.to_csv(buffer, index=False)
            buffer.seek(0)

        elif isinstance(data, str):
            columns = pd.read_csv(data, nrows=1).columns
            buffer = open(data, "rb")

        if buffer is None:
            raise ValueError("Data must be a pandas DataFrame or a file path.")

        data_types_array = []
        data_types_sanitized = []

        for column in columns:
            if column in data_types:
                data_types_array.append(data_types[column])
            else:
                data_types_array.append(DataType.Delete)

        for data_type in data_types_array:
            data_input = {possible: possible == data_type for possible in DataType.All}
            data_types_sanitized.append(data_input)

        if custom_models is None:
            custom_models = [None for _ in range(len(data_types_sanitized))]

        assert len(custom_models) == len(
            data_types_sanitized
        ), "Custom models must align with the sanitized data_types ordering"

        space_id = str(uuid.uuid4())
        file_key = f"{space_name}-{space_id}.{file_extension}"

        resolved_embedding_model = embedding_model or os.environ.get(
            "MANTIS_EMBEDDING_MODEL", "text-embedding-ada-002"
        )
        resolved_chat_model = chat_model or os.environ.get("MANTIS_CHAT_MODEL", "gpt-4o-mini")

        form_data = {
            "space_id": space_id,
            "space_name": space_name,
            "is_public": str(privacy_level == SpacePrivacy.PUBLIC).lower(),
            "red_model": reducer,
            "custom_models": json.dumps(custom_models),
            "data_types": json.dumps(data_types_sanitized),
            "ai_provider": ai_provider,
            "file_key": file_key,
            "chat_model": resolved_chat_model,
            "embedding_model": resolved_embedding_model,
        }

        files = {"file": (f"data.{file_extension}", buffer, f"text/{file_extension}")}

        landscape_response = self._safe_request("POST", "/synthesis/landscape", data=form_data, files=files)
        if isinstance(landscape_response, dict) and landscape_response.get("error"):
            raise RuntimeError(landscape_response["error"])

        layer_id = None
        if isinstance(landscape_response, dict):
            layer_id = landscape_response.get("layer_id", space_id)

        if on_recieve_id is not None:
            on_recieve_id(space_id, layer_id or space_id)

        choseUMAPvariations = False
        previous_progress = -1

        while True:
            progress = self._safe_request("GET", f"synthesis/progress/{space_id}")
            if not isinstance(progress, dict):
                raise RuntimeError("Unexpected progress response format.")

            if progress.get("error"):
                raise SpaceCreationError(progress["error"])

            progress_value = progress.get("progress", 0)

            if progress_value != previous_progress:
                previous_progress = progress_value

            if progress_value >= 50 and not choseUMAPvariations:
                parameters = None

                umap_variations = self._safe_request("GET", f"synthesis/parameters/{space_id}")
                if isinstance(umap_variations, dict):
                    parameters = (
                        umap_variations.get("umap_variations", {}).get("parameters")
                        if umap_variations.get("umap_variations")
                        else None
                    )

                if parameters:
                    chosen_parameter = (
                        self._default_parameter_selection(parameters)
                        if choose_variation is None
                        else choose_variation(parameters)
                    )

                    self._safe_request(
                        "POST",
                        f"synthesis/landscape/{space_id}/select-umap/{chosen_parameter}",
                        rm_slash=True,
                        json={"selected_variation": chosen_parameter, "layer_id": layer_id, "floor_number": 1},
                    )

                    choseUMAPvariations = True

            if progress_value >= 100:
                break

            if progress_value == 0 and choseUMAPvariations:
                raise RuntimeError(
                    "Progress reset to 0 after UMAP selection; possible backend regression or unexpected reset."
                )

            time.sleep(1)

        if layer_id is None:
            layer_id = space_id

        return {"space_id": space_id, "layer_id": layer_id}

@celery.task
def process_space_creation(data):
    try:
        df = pd.DataFrame(data.get('data', {}))

        # Create mantis client with configuration for better timeout handling
        from mantis_sdk.config import ConfigurationManager
        config = ConfigurationManager()
        config.update({
            "host": os.environ.get("MANTIS_HOST", "https://mantisdev.csail.mit.edu"),
            "backend_host": os.environ.get("MANTIS_BACKEND_HOST", "https://mantisdev.csail.mit.edu"),
            "timeout": int(os.environ.get("MANTIS_TIMEOUT", 300000))  # 5 minutes timeout
        })
        
        # Debug cookie information
        cookie = data.get('cookie', '')
        print(f"Cookie length: {len(cookie)}")
        print(f"Cookie preview: {cookie[:100]}...")
        
        if not cookie:
            return {
                "error": "No authentication cookie provided. Please ensure you are logged in to Mantis.",
                "error_type": "authentication_missing"
            }
        
        mantis = ResilientMantisClient("/api/proxy/", cookie, config)

        # Name of connection to create
        name = data.get('name', "Connection") or "Connection"

        def on_recieve_id(space_id, layer_id):
            # Get job ID, exit if not found
            job_id = data.get("job")
            if job_id is None:
                return
            
            # Update the cache with the specific job as a unique dict and store the space_id and layer_id
            redis_cache.hset(f"job_space_id:{job_id}", "space_id", space_id)
            redis_cache.hset(f"job_space_id:{job_id}", "layer_id", layer_id)

        # Prepare custom models for each data type
        data_types = data.get('data_types', {})

        # Tianxi, added specifc supported model types with parameter custom_models
        custom_models = ["text-embedding-ada-002" for _ in data_types.keys()]
        
        # Check data size to prevent timeout issues
        if len(df) < 100:
            return {
                "error": f"Dataset too small. Only {len(df)} rows provided, but minimum 100 rows are required for meaningful visualization.",
                "error_type": "insufficient_data",
                "row_count": len(df)
            }
        
        # If dataset is too large, sample it to prevent timeouts
        # Use very aggressive sampling to prevent timeouts
        if len(df) > 2000:
            return {
                "error": f"Dataset too large. {len(df)} rows provided, but maximum 2,000 rows are recommended to prevent timeouts.",
                "error_type": "dataset_too_large", 
                "row_count": len(df)
            }

        if len(df) > 1000:
            print(f"Dataset has {len(df)} rows. Sampling to 1000 rows to prevent timeouts.")
            df = df.sample(n=1000, random_state=42).reset_index(drop=True)
        
        # Use Mantis SDK for centralized space creation
        space_name = name + " - " + str(uuid.uuid4())
        
        # Convert data_types dict to the format expected by SDK
        # data_types_dict = {}
        # for column, data_type in data_types.items():
        #     data_types_dict[column] = data_type
        
        # Additional optimization: remove any completely empty columns
        df = df.dropna(axis=1, how='all')
        
        # Additional optimization: truncate very long text fields to reduce processing time
        for column in df.columns:
            if df[column].dtype == 'object':  # Text columns
                df[column] = df[column].astype(str).str[:1000]  # Truncate to 1000 characters
        
        # Additional optimization: remove rows with all NaN values
        df = df.dropna(how='all')
        
        # Log the final dataset size
        print(f"Final dataset size: {len(df)} rows, {len(df.columns)} columns")
        
        # Create space using SDK with timeout handling and retry mechanism
        max_retries = 2
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                space_result = mantis.create_space(
                    space_name=space_name,
                    data=df,
                    data_types=data_types_dict,
                    custom_models=custom_models,
                    reducer=ReducerModels.UMAP,
                    privacy_level=SpacePrivacy.PRIVATE,
                    ai_provider=AIProvider.OpenAI,
                    on_recieve_id=on_recieve_id
                )
                break  # Success, exit retry loop
            except RuntimeError as e:
                if "504" in str(e) or "Gateway Time-out" in str(e) or "timeout" in str(e).lower():
                    retry_count += 1
                    if retry_count <= max_retries:
                        print(f"Timeout error occurred, retrying... (attempt {retry_count}/{max_retries})")
                        # Reduce dataset size for retry - use very small samples
                        if len(df) > 500:
                            df = df.sample(n=500, random_state=42).reset_index(drop=True)
                            print(f"Reduced dataset to {len(df)} rows for retry")
                        continue
                    else:
                        return {
                            "error": "Request timed out after multiple retries. The dataset may be too large or the server is under heavy load. Please try again later or with a smaller dataset.",
                            "error_type": "timeout",
                            "retry_count": retry_count,
                            "stacktrace": traceback.format_exc()
                        }
                else:
                    raise e
        
        # Extract space_id from result
        space_id = space_result["space_id"]
        
        # For compatibility, we need to get the layer_id from the result
        # The SDK's create_space method should return both space_id and layer_id
        layer_id = space_result.get("layer_id", space_id)
        
        # Return a simplified response
        # Return a simplified response
        space_response = {
            "space_id": space_id,
            "layer_id": layer_id
        }
            
        return space_response
    except Exception as e:
        return {"error": str(e), "stacktrace": traceback.format_exc()}
