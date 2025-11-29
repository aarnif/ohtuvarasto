import os
from flask import Flask, render_template, request, redirect, url_for, flash
from varasto import Varasto

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

inventories = {}
next_id = 1


@app.route('/')
def index():
    return render_template('index.html', inventories=inventories)


@app.route('/inventory/create', methods=['POST'])
def create_inventory():
    global next_id
    name = request.form.get('name', '').strip()
    capacity_str = request.form.get('capacity', '0')
    initial_str = request.form.get('initial', '0')

    try:
        capacity = float(capacity_str)
        initial = float(initial_str)
    except ValueError:
        flash('Virheellinen arvo.', 'error')
        return redirect(url_for('index'))

    if not name:
        flash('Nimi on pakollinen.', 'error')
        return redirect(url_for('index'))

    if capacity <= 0:
        flash('Tilavuuden tulee olla positiivinen.', 'error')
        return redirect(url_for('index'))

    varasto = Varasto(capacity, initial)
    inventories[next_id] = {'name': name, 'varasto': varasto}
    next_id += 1

    flash(f'Varasto "{name}" luotu.', 'success')
    return redirect(url_for('index'))


@app.route('/inventory/<int:inventory_id>')
def view_inventory(inventory_id):
    if inventory_id not in inventories:
        flash('Varastoa ei löydy.', 'error')
        return redirect(url_for('index'))

    inventory = inventories[inventory_id]
    return render_template(
        'inventory.html',
        inventory=inventory,
        inventory_id=inventory_id
    )


@app.route('/inventory/<int:inventory_id>/update', methods=['POST'])
def update_inventory(inventory_id):
    if inventory_id not in inventories:
        flash('Varastoa ei löydy.', 'error')
        return redirect(url_for('index'))

    name = request.form.get('name', '').strip()
    if not name:
        flash('Nimi on pakollinen.', 'error')
        return redirect(url_for('view_inventory', inventory_id=inventory_id))

    inventories[inventory_id]['name'] = name
    flash('Varasto päivitetty.', 'success')
    return redirect(url_for('view_inventory', inventory_id=inventory_id))


@app.route('/inventory/<int:inventory_id>/add', methods=['POST'])
def add_to_inventory(inventory_id):
    if inventory_id not in inventories:
        flash('Varastoa ei löydy.', 'error')
        return redirect(url_for('index'))

    try:
        amount = float(request.form.get('amount', '0'))
    except ValueError:
        flash('Virheellinen määrä.', 'error')
        return redirect(url_for('view_inventory', inventory_id=inventory_id))

    if amount <= 0:
        flash('Määrän tulee olla positiivinen.', 'error')
        return redirect(url_for('view_inventory', inventory_id=inventory_id))

    inventories[inventory_id]['varasto'].lisaa_varastoon(amount)
    flash(f'Lisättiin {amount} varastoon.', 'success')
    return redirect(url_for('view_inventory', inventory_id=inventory_id))


@app.route('/inventory/<int:inventory_id>/remove', methods=['POST'])
def remove_from_inventory(inventory_id):
    if inventory_id not in inventories:
        flash('Varastoa ei löydy.', 'error')
        return redirect(url_for('index'))

    try:
        amount = float(request.form.get('amount', '0'))
    except ValueError:
        flash('Virheellinen määrä.', 'error')
        return redirect(url_for('view_inventory', inventory_id=inventory_id))

    if amount <= 0:
        flash('Määrän tulee olla positiivinen.', 'error')
        return redirect(url_for('view_inventory', inventory_id=inventory_id))

    taken = inventories[inventory_id]['varasto'].ota_varastosta(amount)
    flash(f'Otettiin {taken} varastosta.', 'success')
    return redirect(url_for('view_inventory', inventory_id=inventory_id))


@app.route('/inventory/<int:inventory_id>/delete', methods=['POST'])
def delete_inventory(inventory_id):
    if inventory_id not in inventories:
        flash('Varastoa ei löydy.', 'error')
        return redirect(url_for('index'))

    name = inventories[inventory_id]['name']
    del inventories[inventory_id]
    flash(f'Varasto "{name}" poistettu.', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
