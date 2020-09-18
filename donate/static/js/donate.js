jQuery(function ($) {
  function displayError(form) {
    genericerrmsg = 'Something went wrong. Please try a different <a href="https://www.noisebridge.net/wiki/Donate_or_Pay_Dues">payment method</a>.'
    $(".alerts").prepend('<div class="alert alert-danger" role="alert">' + genericerrmsg + "</div>");
  };

  function resetErrors(form) {
    form.find(".has-error").removeClass("has-error")
    $(".alerts").empty();
  };

  function validate_fields(fields) {
    var d;
    for (var k in fields) {
      d = fields[k];
      if (typeof d !== "string") {
        return "No " + k.replace("_", " ") + " value entered.";
      }
      if (!(/^[0-9]+$/g).test(d)) {
        return "Invalid credit card " + k.replace("_", " ") + " value.";
      }
    }
  }

  $("form.donation-form").submit(function (event) {
    event.preventDefault();
    var $form = $(this);
    resetErrors($form);
    $form.find("button").prop("disabled", true);


    var fields = {
      number: $form.find(".cc-number").val(),
      cvc: $form.find(".cc-cvc").val(),
      exp_month: $form.find(".cc-exp").val().split("/")[0],
      exp_year: $form.find(".cc-exp").val().split("/")[1]
    };
    var validation_err = validate_fields(fields);

    if (validation_err) {
      $(".alerts").prepend('<div class="alert alert-danger" role="alert">' + validation_err + "</div>");
      return false;
    }

    Stripe.card.createToken(fields, function (status, response) {
      if (response.error) {
        displayError($form);
        $form.find("button").prop("disabled", false);
      }
      else {
        grecaptcha.ready(function() {
          grecaptcha.execute('6LeP9cYZAAAAAOZ0ltHOuM_h7N2DzOpRg6FLqSJ6', {action: 'submit'}).then(function(token) {
            $form.append($('<input type="hidden" name="donor[stripe_token]" />').val(response.id));
            $form.append($('<input type="hidden" name="g-recaptcha-response" />').val(token));
            $form.get(0).submit();
          });
        });
      }
    });

    return false;
  });

  // Allow for custom amounts when "Other" selected in donation amount dropdown
  $("form.donation-form select").on("change", function (e) {
    if ($(this).val() === "other") {
      $("form.donation-form #donation-form-custom-amount").show();
    }
    else {
      $("form.donation-form #donation-form-custom-amount").hide();
    }
  });

  // Enable/disable name input when anonymous option is ticked
  $("#donation-form-anonymous").on("change", function (e) {
    $("#donation-form-name").prop("disabled", $(this).prop("checked"));
    $("#donation-form-name").prop("required", $(this).prop("checked"));
  });
});
