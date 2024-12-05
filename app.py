from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from models import db, Product, Order, OrderItem

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return redirect(url_for('products'))

@app.route('/products')
def products():
    products = Product.select()
    return render_template('products.html', products=products)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    product_id_str = str(product_id)

    cart[product_id_str] = cart.get(product_id_str, 0) + 1
    session['cart'] = cart

    product = Product.get_by_id(product_id)
    quantity = cart[product_id_str]
    subtotal = product.price * quantity
    total = sum(Product.get_by_id(int(pid)).price * qty for pid, qty in cart.items())

    return jsonify({
        'updated_quantity': quantity,
        'updated_subtotal': subtotal,
        'total_items': sum(cart.values()),
        'total': total
    })

@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0

    for product_id_str, quantity in cart.items():
        product_id = int(product_id_str)
        product = Product.get_by_id(product_id)
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': product.price * quantity
        })
        total += product.price * quantity

    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/reduce_quantity/<int:product_id>', methods=['POST'])
def reduce_quantity(product_id):
    cart = session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str] -= 1
        if cart[product_id_str] <= 0:
            del cart[product_id_str]
        session['cart'] = cart

    product = Product.get_by_id(product_id)
    updated_quantity = cart.get(product_id_str, 0)
    updated_subtotal = updated_quantity * product.price if updated_quantity > 0 else 0
    total = sum(Product.get_by_id(int(pid)).price * qty for pid, qty in cart.items())

    return jsonify({
        'updated_quantity': updated_quantity,
        'updated_subtotal': updated_subtotal,
        'total_items': sum(cart.values()),
        'total': total
    })

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        session['cart'] = cart

    total = sum(Product.get_by_id(int(pid)).price * qty for pid, qty in cart.items())
    return jsonify({'total_items': sum(cart.values()), 'total': total})

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash("Your cart is empty.")
        return redirect(url_for('products'))

    if request.method == 'POST':
        customer_name = request.form['name']
        customer_email = request.form['email']
        customer_address = request.form['address']

        order = Order.create(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_address=customer_address
        )

        for product_id_str, quantity in cart.items():
            product_id = int(product_id_str)
            product = Product.get_by_id(product_id)

            if product.stock >= quantity:
                product.stock -= quantity
                product.save()

                subtotal = product.price * quantity
                OrderItem.create(order=order, product=product, quantity=quantity, subtotal=subtotal)
            else:
                flash(f"Not enough stock for {product.name}.")
                return redirect(url_for('cart'))

        session.pop('cart', None) 
        flash(f"Order placed successfully! Thank you, {customer_name}.")
        return redirect(url_for('order_history'))

    total = sum(Product.get_by_id(int(product_id)).price * quantity for product_id, quantity in cart.items())
    return render_template('checkout.html', total=total)


@app.route('/order_history')
def order_history():
    orders = Order.select().order_by(Order.created_at.desc())
    return render_template('order_history.html', orders=orders)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        name = request.form['name']
        price = int(request.form['price'])
        stock = int(request.form['stock'])
        Product.create(name=name, price=price, stock=stock)
        flash("Product added successfully!")
        return redirect(url_for('admin_panel'))

    products = Product.select()
    return render_template('admin.html', products=products)

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    """Delete a product from the database."""
    product = Product.get_by_id(product_id)
    product.delete_instance()
    flash("Product deleted successfully!")
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True)
