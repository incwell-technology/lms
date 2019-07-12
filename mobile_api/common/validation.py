def validation(request):
    has_data = 0
    for d in request.data:
        if d == "first_name":
            has_data += 1
        if d == "last_name":  
            has_data += 1
        if d == "username":  
            has_data += 1
        if d == "email":  
            has_data += 1
        if d == "department":  
            has_data += 1
        if d == "date_of_birth":  
            has_data += 1
        if d == "joined_date":  
            has_data += 1
        if d == "password":  
            has_data += 1
    if has_data < 8:
        return False
    else:
        print(has_data)
        return True
