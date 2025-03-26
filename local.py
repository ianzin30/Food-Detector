##################################################################################################
# Configurações: ajuste de autenticação, ID de modelo e caminho da imagem local
##################################################################################################

# Substitua pelo seu Personal Access Token (encontrado em "Account" -> "Security" no site do Clarifai)
import os
from dotenv import load_dotenv

# Substitua pelo seu Personal Access Token (encontrado em "Account" -> "Security" no site do Clarifai)
load_dotenv()  # Load environment variables from .env

PAT = os.getenv('CLARIFAI_PAT')
if not PAT:
    raise Exception("Please set the CLARIFAI_PAT environment variable.")

# Se você está usando o modelo público do Clarifai, mantenha user_id="clarifai" e app_id="main"
USER_ID = 'clarifai'
APP_ID = 'main'

# Modelo de detecção de comida (Food)
MODEL_ID = 'food-item-recognition'

# Caminho para a sua imagem local
LOCAL_IMAGE_PATH = 'teste4.jpg'

##################################################################################################
# Código de inferência usando gRPC
##################################################################################################

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2

# Cria o canal de comunicação gRPC
channel = ClarifaiChannel.get_grpc_channel()
stub = service_pb2_grpc.V2Stub(channel)

# Metadados de autenticação, usando seu PAT
metadata = (('authorization', 'Key ' + PAT),)

# Objeto que identifica qual usuário e qual aplicação estamos usando
userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

# Lê o arquivo local em bytes
with open(LOCAL_IMAGE_PATH, "rb") as f:
    file_bytes = f.read()

# Cria e envia a requisição de previsão, agora com base64 = file_bytes
post_model_outputs_response = stub.PostModelOutputs(
    service_pb2.PostModelOutputsRequest(
        user_app_id=userDataObject,
        model_id=MODEL_ID,
        inputs=[
            resources_pb2.Input(
                data=resources_pb2.Data(
                    image=resources_pb2.Image(
                        base64=file_bytes  # Envia a imagem local em bytes
                    )
                )
            )
        ]
    ),
    metadata=metadata
)

# Verifica se a requisição deu certo
if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
    print(post_model_outputs_response.status)
    raise Exception("Falha ao obter resultados do modelo: " + 
                    post_model_outputs_response.status.description)

# Como enviamos apenas 1 input, teremos apenas 1 output
output = post_model_outputs_response.outputs[0]

print("Conceitos previstos (itens de comida e probabilidades):")
for concept in output.data.concepts:
    print(f"- {concept.name}: {concept.value:.2f}")

# Se quiser ver a resposta JSON completa, descomente a linha abaixo:
# print(output)
