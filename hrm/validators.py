
class NameValidator:
    def __init__(self, name: str, _: str):
        self.is_valid = False
        if name:
            stripped_name = name.strip()
            if stripped_name.isalpha():
                self.is_valid = True
                self.cleaned_name = stripped_name
            else:
                self.error_message = 'only alphabetic characters are allowed'
        else:
            self.error_message = _ + ' name cannot be empty'
