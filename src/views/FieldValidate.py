

class FieldValidate:
    @staticmethod
    def int_restrict(p_entry_value):
        if p_entry_value == '':
            return True
        if p_entry_value == '0':
            return True
        if p_entry_value.isnumeric():
            return True
        return False

    @staticmethod
    def float_restrict(p_entry_value):
        """ This should probably just be a regular expression, need to research that in the future. """
        try:
            if p_entry_value == '':
                return True
            if p_entry_value == '0':
                return True
            if p_entry_value == '.' or p_entry_value == '.0' or p_entry_value == '.00' or \
                    p_entry_value == '.000' or p_entry_value == '.0000' or p_entry_value == '.00000':
                return True
            if p_entry_value == '0.' or p_entry_value == '0.0' or p_entry_value == '0.00' or \
                    p_entry_value == '0.000' or p_entry_value == '0.0000' or p_entry_value == '0.00000':
                return True
            if float(p_entry_value):
                return True
            return False
        except ValueError:
            return False
