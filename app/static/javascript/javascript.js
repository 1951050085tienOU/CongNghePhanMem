let customerPhoneNumber = ''
let user = null

function CheckSession(idModal) { //user, phoneNumber,
    id = idModal.substring(3);
    //if user exist
    if (user) { //bo 'bt-' ra khoi id cua button
        $("#" + idModal).attr("data-target", '#' + id);
    }
    else {
        $("#" + idModal).attr("data-target", '#login-require');
    }
}
