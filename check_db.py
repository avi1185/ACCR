from app import app, db, City, DepartmentContact

with app.app_context():
    cities = City.query.all()
    contacts = DepartmentContact.query.all()
    
    print(f"Number of cities: {len(cities)}")
    if cities:
        print(f"First city: {cities[0].name}, {cities[0].state}")
    
    print(f"\nNumber of department contacts: {len(contacts)}")
    if contacts:
        contact = contacts[0]
        print(f"First contact: {contact.department_name}")
        print(f"Email: {contact.email}")
        print(f"Phone: {contact.toll_free_number}")
        print(f"Address: {contact.office_address}") 