class UserIDGenerator:
    def __init__(self):
        self.current_id = 0

    def generate_userid(self):
        self.current_id += 1
        return self.current_id
    
user_id_generator = UserIDGenerator()

print(user_id_generator.generate_userid())
# print(user_id_generator.generate_userid())