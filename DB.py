import json

class Database:

    def import_data(self,email,mobile,name,password):

        with open("user_data.json","r") as file:
            user=json.load(file)

            if(email in user):
                return 0
            else:
                user[email]=[name,mobile,password]
                
        with open("user_data.json",'w') as new_data:
            json.dump(user,new_data,indent=4)
            return 1
        
    def check(self,email,password):
        with open("user_data.json","r") as data:
            user=json.load(data)

            if(email in user):
                if(password in user[email]):
                    return 1
                else:
                    return 0
            else:
                return 0