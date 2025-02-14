import asyncio
import mantis_sdk.config as config

config.HOST = "https://mantisdev.csail.mit.edu"
config.DOMAIN = "mantisdev.csail.mit.edu"

from mantis_sdk.client import MantisClient, SpacePrivacy, DataType, ReducerModels
from mantis_sdk.space import Space
from mantis_sdk.render_args import RenderArgs

async def main():
	client = MantisClient ("/api/proxy/", "MIT_PressMachineID=638695455057712972; fpestid=y_jCLhNDgF9Sl8XTsHV4RVkCavCXEfFAye1gwdskq0XB1Ld-t2d3Kfct4Sziqmm4z37ANQ; _gcl_au=1.1.1818488075.1733948708; _ga=GA1.2.1626376916.1733948708; _cc_id=87e78069c8ef999b8a9bee266d763eb; _fbp=fb.1.1733948708594.560146927926962738; hum_mit_visitor=626c6e0b-d291-445b-ac5f-ef3af434480b; hum_mit_synced=true; _ga_VJ81RKXDL1=GS1.1.1733948708.1.0.1733948744.24.0.0; ph_phc_twLBfXCcnUBL6puODlvhWgNBNBMXKJAndCeqb957mO9_posthog=%7B%22distinct_id%22%3A%22lbvoros%40gmail.com%22%2C%22%24sesid%22%3A%5B1736968586799%2C%2201946b50-b62e-78ba-8906-74086c0a5583%22%2C1736967239214%5D%2C%22%24epp%22%3Atrue%2C%22%24initial_person_info%22%3A%7B%22r%22%3A%22%24direct%22%2C%22u%22%3A%22https%3A%2F%2Fmantisdev.csail.mit.edu%2Fhome%2F%22%7D%7D; csrftoken=BdIE4uUe60GpRLfqaaMVr480ZVEcecWZ; __Host-next-auth.csrf-token=5d6088764a5d1e86bce942376fa1f9c14d9fc0346ea1e465fc31638c9b216ab6%7Ce76f7a899cf6be4af010d0fe51d749f077739fc99da0ed8c8c828b73fa69de11; __Secure-next-auth.callback-url=https%3A%2F%2Fmantisdev.csail.mit.edu; sessionid=wkzkf2jolbgw8oquofmwbqeooaoyke12; __Secure-next-auth.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..HI4NJZegOaX8Ujjp.eI618_VeusvXtWm0eKmQ1if8V2UKxCpWZIVGN5egfo9akrV9TXmim60I_Xl9sINQegpXU9OoyW2WAkbucNUKRp5I27w6nY0ipHBqUOi79t390-WcsbH4KcJ_7AVk3uPXjb7ex0gVJ1dHOYOV7Fl7WL4QdVQCi8APaOVvkHDP2soerTYhvpjAg8BXzbh8J9iGKUC3HF94D7bYETqow0efRdb-7z6-Hq-TXqIxMkUTgrHcL2QToqYgsOsyKLLrIHb-g0_1ObNh1oo6iHremV2jBBd41-aQqo3bujkBpMxWVVD6oPaWqQlyBVYVNSHA4T8eaqXYOxmZYpqUDtOy-KGTKAoHSQhOMW6lgh0cZWdn5GZT-8zU7MQ90fuddA.o_msrbN_3EZZMs_OeAK0VA; ph_phc_xKneBiNcXuoXtSlj6ZGCwvlVtHsjuQ8vAAhax5GL0VM_posthog=%7B%22distinct_id%22%3A%22lbvoros%40gmail.com%22%2C%22%24sesid%22%3A%5B1739494386003%2C%22019501f1-e2b4-7866-ac9a-94c0d9f2f653%22%2C1739494384308%5D%2C%22%24epp%22%3Atrue%2C%22%24initial_person_info%22%3A%7B%22r%22%3A%22%24direct%22%2C%22u%22%3A%22https%3A%2F%2Fmantisdev.csail.mit.edu%2Fhome%2F%22%7D%7D")
	space = await client.open_space ("382814c1-45c3-4d0d-9101-ad52b7ce7a27")

if __name__ == '__main__':
	asyncio.run(main())