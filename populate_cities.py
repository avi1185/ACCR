from app import app, db, City, DepartmentContact
import json

# Sample data for major Indian cities and their department contacts
CITIES_DATA = {
    "Maharashtra": {
        "Mumbai": {
            "Electricity Board": {
                "email": "help.merc@mercindia.org.in",
                "toll_free": "1800-233-3435",
                "address": "World Trade Centre, Centre No.1, 13th Floor, Cuffe Parade, Mumbai - 400005"
            },
            "Public Works Department": {
                "email": "pwdmumbai@maharashtra.gov.in",
                "toll_free": "1800-220-233",
                "address": "PWD Office, Bandhkam Bhavan, 25, Murzban Road, Fort, Mumbai - 400001"
            },
            # Add other departments
        },
        "Pune": {
            "Electricity Board": {
                "email": "msedcl.pune@gmail.com",
                "toll_free": "1800-233-3435",
                "address": "MSEDCL, 565, Rasta Peth, Pune - 411011"
            },
            # Add other departments
        }
    },
    "Delhi": {
        "New Delhi": {
            "Electricity Board": {
                "email": "brpl.customercare@relianceada.com",
                "toll_free": "1800-102-4001",
                "address": "BSES Rajdhani Power Limited, BSES Bhawan, Nehru Place, New Delhi - 110019"
            },
            # Add other departments
        }
    },
    # Add more states and cities
}

def populate_cities():
    with app.app_context():
        # Clear existing data
        DepartmentContact.query.delete()
        City.query.delete()
        
        # Add cities and department contacts
        for state, cities in CITIES_DATA.items():
            for city_name, departments in cities.items():
                city = City(name=city_name, state=state)
                db.session.add(city)
                db.session.flush()  # Get city ID
                
                for dept_name, contact in departments.items():
                    dept_contact = DepartmentContact(
                        city_id=city.id,
                        department_name=dept_name,
                        email=contact['email'],
                        toll_free_number=contact['toll_free'],
                        office_address=contact['address']
                    )
                    db.session.add(dept_contact)
        
        db.session.commit()
        print("Cities and department contacts populated successfully!")

if __name__ == '__main__':
    populate_cities() 