from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from accounts.models import User

class UserCreateForm(UserCreationForm):

    class Meta:

        model = User
        fields = (
            'username', 'first_name', 
            'last_name', 'password1', 
            'password2',
            )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username'
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Repeat Password'


class LoginForm(AuthenticationForm):

    class Meta:

        fields = ('username', 'password')
        model = User

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Username"
        self.fields['password'].label = "Password"
        self.fields['username'].widget.attrs['placeholder'] = 'Type your username'
        self.fields['password'].widget.attrs['placeholder'] = 'Type your password'