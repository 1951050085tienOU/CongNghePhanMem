let customerPhoneNumber = ''
let user = null

function CheckSession(user, idModal) { //user, phoneNumber,
    id = idModal.substring(3);
    //if user exist
    if (user) { //bo 'bt-' ra khoi id cua button
        $("#" + idModal).attr("data-target", '#' + id);
    }
    else {
        $("#" + idModal).attr("data-target", '#login-require');
    }
}
function CheckPhoneNumber(phoneNumber, again) {
    document.getElementById('otp-code').value = ""
    if (phoneNumber.startsWith('84') && phoneNumber.length == 11 || phoneNumber.startsWith('0') && phoneNumber.length == 10) {
        document.getElementById('customerPhoneNumber-status').textContent = '';
        if (again==false)
            OTPSendCode(phoneNumber);
        else OTPSendCodeAgain(phoneNumber);
    }
    else if (phoneNumber.length > 0)
        document.getElementById('customerPhoneNumber-status').textContent = 'Số điện thoại không hợp lệ';
    else
        document.getElementById('customerPhoneNumber-status').textContent = null;
}
function OTPSendCode(phoneNumber) {
    event.preventDefault()

    fetch("/api/otp-auth", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'phoneNumber': phoneNumber
        })
    })
}
function OTPSendCodeAgain(phoneNumber) {
    event.preventDefault()

    fetch("/api/otp-auth-again", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'phoneNumber': phoneNumber
        })
    })
}
function ValidatePhoneNumber(OTPValue, idFormSubmit) {
    phoneNumber = document.getElementById('customerPhoneNumber').value.toString();
    if (phoneNumber.startsWith('84') && phoneNumber.length == 11 || phoneNumber.startsWith('0') && phoneNumber.length == 10) {
        if (OTPValue.length == 6)
        {
            $('#' + idFormSubmit).submit()
        }
    }
}