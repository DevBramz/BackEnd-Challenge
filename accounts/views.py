from django.shortcuts import render

from rest_framework.response import Response
from rest_framework import status

from rest_framework.authtoken.models import Token
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated, )
from .serializers import (LoginSerializer, RegistrationSerializer,)
from rest_framework.views import APIView

# Create your views here.
class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    # renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    # @swagger_auto_schema(request_body=RegistrationSerializer,
    #                      responses={
    #                          201: UserSerializer()})
    def post(self, request):
        # user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # token = serializer.instance.token

        # Send a verification email to the user
        # The combination of the token and uidb64 makes sure that the user
        # has a unique verification link that expires in 7 days by default
        # subject = "Email Verification"
        # self._kwargs = {
        #     'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
        #     'token': email_activation_token.make_token(user)
        # }

        # url = self.get_email_verification_url(request)

        # context = {'username': user.username,
        #            'url': url}
        # message = render_to_string('verify.html', context)
        # recipients = [user.email, ]
        # msg = EmailMultiAlternatives(
        #     subject, message, 'ah.centauri@gmail.com', recipients)
        # msg.attach_alternative(message, "text/html")
        # msg.send()

        return Response({
            # "token": token,
            "message": f"A verification email has been sent to {user.email}",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    # def get_email_verification_url(self, request):

    #     base_url = settings.EMAIL_VERIFICATION_BASE_URL

    #     uid = self._kwargs.get('uidb64')
    #     token = self._kwargs.get('token')

    #     if base_url:
    #         return f"{request.scheme}://{base_url}/{token}/{uid}"

    #     verification_url = reverse(
    #         'authentication:verify', kwargs=self._kwargs)

    #     return f"{request.scheme}://{request.get_host()}{verification_url}"


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    # renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    # @swagger_auto_schema(request_body=LoginSerializer,
    #                      responses={
    #                          200: UserSerializer()})
    def post(self, request):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        
        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        # serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        user= serializer.validated_data['user']
        print(serializer.validated_data)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'message': "you have successfully logged in!"
        }, status=status.HTTP_200_OK)
