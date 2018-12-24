jQuery(function ($) {
  function displayError(form, error) {
    $(".alerts").prepend('<div class="alert alert-danger" role="alert">' + error.message + "</div>");
    form.find("[data-stripe=" + error.param + "]").closest(".form-group").addClass("has-error");
  };

  function resetErrors(form) {
    form.find(".has-error").removeClass("has-error")
    $(".alerts").empty();
  };

  $("form.donation-form").submit(function (event) {
    event.preventDefault();
    var $form = $(this);
    resetErrors($form);
    $form.find("button").prop("disabled", true);

    Stripe.card.createToken({
      number: $form.find(".cc-number").val(),
      cvc: $form.find(".cc-cvc").val(),
      exp_month: $form.find(".cc-exp"),
      exp_year: $form.find(".cc-exp")
    }, function (status, response) {
      if (response.error) {
        displayError($form, response.error);
        $form.find("button").prop("disabled", false);
      } 
      else {
        $form.append($('<input type="hidden" name="donor[stripe_token]" />').val(response.id));
        $form.get(0).submit();
      }
    });

    return false;
  });

  // Allow for custom amounts when "Other" selected in donation amount dropdown
  $("form.donation-form select").on("change", function (e) {
    if ($(e.target).val() == "other") {
      $("form.donation-form .form-group.amount")
        .append($("#donation-form-custom-amount").html())
    }
    else {
      $("form.donation-form .custom-amount").remove();
    }
  });
});
