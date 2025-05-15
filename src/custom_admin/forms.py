from django import forms
from django.contrib.auth.models import User
from data_access.models import Book, Review
from django.core.exceptions import ValidationError

class BookForm(forms.ModelForm):
    """Form for creating and editing books."""
    
    # Convert comma-separated categories string to list
    categories = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'}),
        help_text="Separate categories with commas",
        required=False
    )
    
    class Meta:
        model = Book
        fields = ['title', 'authors', 'description', 'categories', 'image', 'publisher', 'publishedDate']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'}),
            'authors': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500', 'rows': 4}),
            'image': forms.URLInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'}),
            'publisher': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'}),
            'publishedDate': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'}),
        }
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        
        # Convert categories list to comma-separated string for the form
        if instance and hasattr(instance, 'categories') and instance.categories:
            if isinstance(instance.categories, list):
                # Create a copy of the initial data to avoid modifying the instance
                initial = kwargs.get('initial', {}).copy()
                initial['categories'] = ', '.join(instance.categories)
                kwargs['initial'] = initial
        
        super().__init__(*args, **kwargs)
    
    def clean_categories(self):
        """Convert comma-separated categories to a list."""
        categories_text = self.cleaned_data.get('categories', '')
        if not categories_text:
            return []
        
        # Split by comma and strip whitespace
        categories = [cat.strip() for cat in categories_text.split(',') if cat.strip()]
        return categories
    
    def save(self, commit=True):
        """Override save to handle the categories field."""
        instance = super().save(commit=False)
        
        # Save categories as a list
        instance.categories = self.cleaned_data.get('categories', [])
        
        if commit:
            instance.save()
        
        return instance


class UserForm(forms.ModelForm):
    """Form for creating and editing users."""
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'}),
        required=False,
        help_text="Leave empty if you don't want to change the password."
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'}),
        required=False,
        help_text="Enter the same password as above, for verification."
    )
    role = forms.ChoiceField(
        label="Role",
        choices=[
            ('reader', 'Reader'),
            ('staff', 'Staff'),
            ('admin', 'Admin')
        ],
        widget=forms.Select(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'}),
        required=True
    )
    is_active = forms.BooleanField(
        label="Active account",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 rounded'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        
        # Set initial role value based on user permissions
        if instance:
            if instance.is_superuser:
                self.fields['role'].initial = 'admin'
            elif instance.is_staff:
                self.fields['role'].initial = 'staff'
            else:
                self.fields['role'].initial = 'reader'
                
            # Don't require password for existing users
            self.fields['password1'].required = False
            self.fields['password2'].required = False
        else:
            # Require password for new users
            self.fields['password1'].required = True
            self.fields['password2'].required = True
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password1 != password2:
            self.add_error('password2', "The two password fields didn't match.")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Set user permissions based on role
        role = self.cleaned_data.get('role')
        if role == 'admin':
            user.is_staff = True
            user.is_superuser = True
        elif role == 'staff':
            user.is_staff = True
            user.is_superuser = False
        else:  # reader
            user.is_staff = False
            user.is_superuser = False
        
        # Set password if provided
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
        
        return user


class UserFilterForm(forms.Form):
    """Form for filtering users in the user list view."""
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Search users...', 
        'class': 'w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'
    }))
    role = forms.ChoiceField(required=False, choices=[
        ('', 'All Roles'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('reader', 'Reader')
    ], widget=forms.Select(attrs={
        'class': 'border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'
    }))
    status = forms.ChoiceField(required=False, choices=[
        ('', 'All Status'),
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], widget=forms.Select(attrs={
        'class': 'border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'
    }))


class BookFilterForm(forms.Form):
    """Form for filtering books in the book list view."""
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Search books...', 
        'class': 'w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'
    }))
    category = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Category', 
        'class': 'border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'
    }))
    sort = forms.ChoiceField(required=False, choices=[
        ('title', 'Title A-Z'),
        ('-title', 'Title Z-A'),
        ('publishedDate', 'Oldest First'),
        ('-publishedDate', 'Newest First')
    ], widget=forms.Select(attrs={
        'class': 'border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'
    }))
