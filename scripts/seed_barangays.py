from models import db
from models.barangay import Barangay
from app import create_app

QUEZON_CITY_BARANGAYS = [
    'Alicia', 'Amihan', 'Apolonio Samson', 'Bagbag', 'Bagong Lipunan ng Crame', 'Bagong Pag-asa',
    'Bagong Silangan', 'Bahay Toro', 'Balingasa', 'Balong Bato', 'Batasan Hills', 'Bayanihan',
    'Blue Ridge A', 'Blue Ridge B', 'Botocan', 'Bungad', 'Camp Aguinaldo', 'Capri', 'Central',
    'Claro', 'Commonwealth', 'Culiat', 'Damar', 'Damayan', 'Damayang Lagi', 'Del Monte',
    'Dioquino Zobel', 'Doña Aurora', 'Doña Imelda', 'Doña Josefa', 'Duyan-duyan', 'E. Rodriguez',
    'East Kamias', 'Escopa I', 'Escopa II', 'Escopa III', 'Escopa IV', 'Fairview', 'Greater Lagro',
    'Gulod', 'Horseshoe', 'Holy Spirit', 'Immaculate Conception', 'Kaligayahan', 'Kalusugan',
    'Kamuning', 'Katipunan', 'Kaunlaran', 'Kristong Hari', 'Krus na Ligas', 'Laging Handa',
    'Libis', 'Lourdes', 'Loyola Heights', 'Maharlika', 'Malaya', 'Mangga', 'Manresa', 'Mariana',
    'Mariblo', 'Marilag', 'Masagana', 'Masambong', 'Matandang Balara', 'Milagrosa', 'N.S. Amoranto',
    'Nagkaisang Nayon', 'Nayong Kanluran', 'New Era', 'Novaliches Proper', 'Obrero', 'Old Capitol Site',
    'Paang Bundok', 'Pag-ibig sa Nayon', 'Paligsahan', 'Paltok', 'Pansol', 'Paraiso', 'Pasong Putik Proper',
    'Pasong Tamo', 'Payatas', 'Phil-Am', 'Pinyahan', 'Project 6', 'Quirino 2-A', 'Quirino 2-B',
    'Quirino 2-C', 'Quirino 3-A', 'Ramon Magsaysay', 'Roxas', 'Sacred Heart', 'Salvacion', 'San Agustin',
    'San Antonio', 'San Bartolome', 'San Isidro', 'San Isidro Labrador', 'San Jose', 'San Martin de Porres',
    'San Roque', 'Santa Cruz', 'Santa Lucia', 'Santa Monica', 'Santo Cristo', 'Santo Domingo',
    'Santo Niño', 'Santol', 'Sauyo', 'Sienna', 'Sikatuna Village', 'Silangan', 'Socorro', 'South Triangle',
    'Tagumpay', 'Talayan', 'Tandang Sora', 'Tatalon', 'Teachers Village East', 'Teachers Village West',
    'Ugong Norte', 'Unang Sigaw', 'UP Campus', 'UP Village', 'Valencia', 'Vasra', 'Veterans Village',
    'Villa Maria Clara', 'West Kamias', 'West Triangle'
]

def seed_barangays():
    app = create_app()
    with app.app_context():
        for name in QUEZON_CITY_BARANGAYS:
            if not Barangay.query.filter_by(name=name).first():
                barangay = Barangay(name=name)
                db.session.add(barangay)
        db.session.commit()
        print(f"Seeded {len(QUEZON_CITY_BARANGAYS)} barangays of Quezon City.")

if __name__ == '__main__':
    seed_barangays() 