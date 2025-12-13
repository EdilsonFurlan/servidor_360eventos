
# usuarios/views.py
from datetime import date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import Usuario

from rest_framework.permissions import IsAuthenticated

from datetime import timedelta, date




@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'detail': 'E-mail e senha são obrigatórios.'}, status=400)

    user = authenticate(request, email=email, password=password)
    
    if user is not None:
        if not user.is_active:
            return Response({'detail': 'Esta conta não está ativa.'}, status=401)

        # --- VERIFICAÇÃO DE VENCIMENTO ---
        data_vencimento_str = user.data_vencimento.isoformat() if user.data_vencimento else None
        
        # Gera o token para o usuário (mesmo se expirado)
        token, created = Token.objects.get_or_create(user=user)

        # Se estiver expirado, a gente avisa no 'detail', mas MANDA O TOKEN e status 200
        # O app vai ler a data_vencimento e bloquear o que for necessário visualmente
        if user.data_vencimento and user.data_vencimento < date.today():
             return Response({
                'message': 'Login realizado (Plano Expirado)',
                'token': token.key,
                'user_id': user.id,
                'user_nome': user.nome,
                'data_vencimento': data_vencimento_str,
                'warning': 'Seu plano expirou. Entre em contato para renovar.',
                'video_config': {
                    'video_resolution': user.video_resolution,
                    'video_fps': user.video_fps,
                    'video_bitrate': user.video_bitrate,
                    'video_duration': user.video_duration,
                    'video_camera_lens': user.video_camera_lens
                }
            }, status=200)
        
        # --- LOGIN SUCESSO (Plano Ativo) ---
        return Response({
            'message': 'Login bem-sucedido!',
            'token': token.key,
            'user_id': user.id,
            'user_nome': user.nome,
            'data_vencimento': data_vencimento_str,
            'video_config': {
                'video_resolution': user.video_resolution,
                'video_fps': user.video_fps,
                'video_bitrate': user.video_bitrate,
                'video_duration': user.video_duration,
                'video_camera_lens': user.video_camera_lens
            }
        }, status=200)

    return Response({'detail': 'Credenciais inválidas.'}, status=401)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validate_user(request):
    """
    Endpoint leve apenas para retornar a data de vencimento atualizada.
    O Android usa isso na inicialização para atualizar o cache local.
    """
    user = request.user
    
    # Formata a data para string (igual ao login)
    data_vencimento_str = user.data_vencimento.isoformat() if user.data_vencimento else None
    
    return Response({
        'message': 'Validação realizada',
        'data_vencimento': data_vencimento_str,
        'video_config': {
            'video_resolution': user.video_resolution,
            'video_fps': user.video_fps,
            'video_bitrate': user.video_bitrate,
            'video_duration': user.video_duration,
            'video_camera_lens': user.video_camera_lens
        }
    }, status=200)

    # views.py


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def renovar_assinatura(request):
    dias = request.data.get('dias')

    if not dias:
        return Response({'detail': 'dias é obrigatório'}, status=400)

    user = request.user
    hoje = date.today()

    if user.data_vencimento and user.data_vencimento > hoje:
        user.data_vencimento += timedelta(days=int(dias))
    else:
        user.data_vencimento = hoje + timedelta(days=int(dias))

    user.save()

    return Response({
        'message': 'Atualizado',
        'nova_data': user.data_vencimento.strftime("%Y-%m-%d")
    }, status=200)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_register(request):
    nome = request.data.get('nome')
    email = request.data.get('email')
    password = request.data.get('password')

    if not nome or not email or not password:
        return Response({'detail': 'Nome, email e senha são obrigatórios.'}, status=400)

    if Usuario.objects.filter(email=email).exists():
        return Response({'detail': 'Este email já está cadastrado.'}, status=400)

    try:
        user = Usuario.objects.create_user(email=email, nome=nome, password=password)
        
        # Opcional: Definir data de vencimento inicial (ex: 7 dias grátis)
        # user.data_vencimento = date.today() + timedelta(days=7)
        # user.save()

        token, created = Token.objects.get_or_create(user=user)
        
        data_vencimento_str = user.data_vencimento.isoformat() if user.data_vencimento else None

        return Response({
            'message': 'Cadastro realizado com sucesso!',
            'token': token.key,
            'user_id': user.id,
            'user_nome': user.nome,
            'user_nome': user.nome,
            'data_vencimento': data_vencimento_str,
            'video_config': {
                'video_resolution': user.video_resolution,
                'video_fps': user.video_fps,
                'video_bitrate': user.video_bitrate,
                'video_duration': user.video_duration,
                'video_camera_lens': user.video_camera_lens
            }
        }, status=201)

    except Exception as e:
        return Response({'detail': str(e)}, status=500)
    except Exception as e:
        return Response({'detail': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_video_config(request):
    user = request.user
    
    user.video_resolution = request.data.get('video_resolution', user.video_resolution)
    user.video_fps = request.data.get('video_fps', user.video_fps)
    user.video_bitrate = request.data.get('video_bitrate', user.video_bitrate)
    user.video_duration = request.data.get('video_duration', user.video_duration)
    user.video_camera_lens = request.data.get('video_camera_lens', user.video_camera_lens)
    
    user.save()
    
    return Response({'message': 'Configurações atualizadas'}, status=200)
