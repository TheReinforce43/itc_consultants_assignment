from rest_framework import serializers 
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken 
from django.contrib.auth import authenticate 
User = get_user_model()
from utils import user_roles



# Create User sign Up Serializer 


class UserSignUpSerializer(serializers.ModelSerializer):

    phone_number = serializers.CharField(allow_blank=True, required=False)
    roles = serializers.ChoiceField(choices=user_roles, required=False)
    profile_image = serializers.ImageField(allow_null=True, required=False) 

    class Meta:
        model = User
        fields = ['phone_number', 'email','first_name','last_name', 'password','roles','profile_image']
        extra_kwargs = {
            'password': {'write_only': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }


    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError("Phone number must be between 10 and 15 digits.")
        
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already exists.")
        
        return value

    def create(self, validated_data):
        email= validated_data['email']
        password= validated_data['password']
        phone_number= validated_data.get('phone_number')
        first_name= validated_data.get('first_name')
        last_name= validated_data.get('last_name')
        roles= validated_data.get('roles')
        profile_image= validated_data.get('profile_image')

        user = User.objects.create_user(
            email=email,
            password=password,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            roles=roles,
            profile_image=profile_image
        )

        return user


# Create User Login Serializer 


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    id = serializers.IntegerField(read_only=True)
    phone_number = serializers.CharField(read_only=True)


    def validate(self, attrs):

        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        user = authenticate(email=email, password=password)

        if not  user:
            raise serializers.ValidationError("Invalid email or password.")
        

        # Generate tokens 

        refresh = RefreshToken.for_user(user)

        return {
            'id': user.id,
            'email': user.email,
            'phone_number': user.phone_number,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'roles': user.roles,
        }
    

# User Log Out Serializer 

class UserLogoutSerializer(serializers.Serializer):

    refresh_token = serializers.CharField() 


    def validate(self , data):
        self.refresh_token = data['refresh_token']

        return data 
    
    def save(self,**kwargs):

        try :
            token = RefreshToken(self.refresh_token)
            token.blacklist()
        

        except Exception as E :
            raise serializers.ValidationError("Invalid token or expire")
        
# CLass Get UserSerializer 

class GetUserSerializer(serializers.ModelSerializer):

    class Meta:
        model= User 
        fields = ['phone_number', 'email','first_name','last_name','roles','profile_image']



    
    