FROM odoo:17

# Install deps ringan agar Odoo bisa jalan
USER root
RUN pip3 install --upgrade pip

# (Opsional) Install library tambahan jika perlu
RUN pip install psycopg2-binary

USER odoo

# Copy konfigurasi
COPY odoo.conf /etc/odoo/odoo.conf
COPY addons /mnt/extra-addons
