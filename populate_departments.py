from app import app, db, City, DepartmentContact, INDIAN_CITIES, DEPARTMENT_INFO
import random

def generate_phone():
    """Generate a random toll-free number"""
    return f"1800{random.randint(100000, 999999)}"

def generate_email(city, department):
    """Generate department email for a city"""
    dept_name = department.lower().replace(' ', '')
    city_name = city.lower().replace(' ', '')
    return f"{dept_name}.{city_name}@citysamadhan.gov.in"

def generate_address(city, department):
    """Generate office address for a department"""
    return f"{department} Office, {random.randint(1, 100)} Main Road, {city}"

def populate_departments():
    with app.app_context():
        # First clear existing data
        DepartmentContact.query.delete()
        City.query.delete()
        db.session.commit()

        # Add cities and department contacts
        for state, cities in INDIAN_CITIES['states'].items():
            print(f"Processing state: {state}")
            for city_name in cities:
                print(f"Adding departments for city: {city_name}")
                
                # Create city
                city = City(name=city_name, state=state)
                db.session.add(city)
                db.session.flush()  # Get city ID
                
                # Add department contacts
                for dept_name in DEPARTMENT_INFO.keys():
                    contact = DepartmentContact(
                        city_id=city.id,
                        department_name=dept_name,
                        email=generate_email(city_name, dept_name),
                        toll_free_number=generate_phone(),
                        office_address=generate_address(city_name, dept_name)
                    )
                    db.session.add(contact)
                
                db.session.commit()
                print(f"Added {len(DEPARTMENT_INFO)} departments for {city_name}")

if __name__ == '__main__':
    populate_departments()
    print("Department contacts populated successfully!") 