function toggleProducts() {
    var products = document.querySelectorAll('.product');
    products.forEach(function(product) {
        product.classList.toggle('hidden');
    });
}


function fetchAndDisplayDataProduct(product) {
    fetch(`/product/${product}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            window.location.href = `/product/${product}`;
        })
        .catch(error => console.error('Error fetching data:', error));
}



