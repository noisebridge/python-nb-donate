

function donateHttpGetAsync(value, cback)
{
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            cback(this);
        }
    }
    xhttp.open("GET", "nonce/"+value, true);
    xhttp.send();
}

function initStripe(xhttp) {
    // var data = document.getElementById('special-thing');
    var data = JSON.parse(xhttp.responseText);
    stripe = Stripe.setPublishableKey(data);
}
