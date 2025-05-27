from djoser import email

class PasswordChangedConfirmationEmail(email.PasswordChangedConfirmationEmail):
    template_name = "emails/password_changed_confirmation.html"