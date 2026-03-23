from app import app, db, Admin

def populate_admins():
    with app.app_context():
        # Clear existing admins
        Admin.query.delete()
        db.session.commit()

        # Add dummy admins for different departments and cities
        admins_data = [
            {
                'name': 'Rajesh Kumar',
                'email': 'rajesh.electricity.mumbai@gov.in',
                'password': 'admin123',
                'department': 'Electricity Board',
                'city': 'Mumbai',
                'state': 'Maharashtra'
            },
            {
                'name': 'Priya Sharma',
                'email': 'priya.water.mumbai@gov.in',
                'password': 'admin123',
                'department': 'Water Supply Authority',
                'city': 'Mumbai',
                'state': 'Maharashtra'
            },
            {
                'name': 'Roads Admin',
                'email': 'iamqwertyui11@gmail.com',
                'password': 'admin123',
                'department': 'Public Works Department',
                'city': 'Mumbai',
                'state': 'Maharashtra'
            },
            {
                'name': 'Amit Singh',
                'email': 'amit.roads.pune@gov.in',
                'password': 'admin123',
                'department': 'Public Works Department',
                'city': 'Pune',
                'state': 'Maharashtra'
            },
            {
                'name': 'Sneha Patel',
                'email': 'sneha.electricity.bangalore@gov.in',
                'password': 'admin123',
                'department': 'Electricity Board',
                'city': 'Bangalore',
                'state': 'Karnataka'
            },
            {
                'name': 'Vikram Rao',
                'email': 'vikram.waste.bangalore@gov.in',
                'password': 'admin123',
                'department': 'Municipal Waste Management',
                'city': 'Bangalore',
                'state': 'Karnataka'
            }
        ]

        for admin_data in admins_data:
            admin = Admin(**admin_data)
            db.session.add(admin)
            print(f"Added admin: {admin_data['name']} for {admin_data['department']} in {admin_data['city']}")

        db.session.commit()
        print("All admins added successfully!")

if __name__ == '__main__':
    populate_admins()