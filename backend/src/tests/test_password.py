import bcrypt

password = "securepassword123"
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print("Hashed password:", hashed_password)
