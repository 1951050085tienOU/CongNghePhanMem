function add_new_medicalBill(new_customer_name, new_phoneNumber, new_age, new_gender,
            new_maPhieuKham, new_symptom, new_diagnostic_disease, new_how_to_use, new_medicine_name) {

    event.preventDefault();

    fetch('/api/new-regulation', {
        method: 'post',
        body: JSON.stringify({
            'new_customer_name': new_customer_name,
            'new_phoneNumber': new_phoneNumber,
            'new_age': new_age,
            'new_gender': new_gender,
            'new_maPhieuKham': new_maPhieuKham,
            'new_symptom': new_symptom,
            'new_diagnostic_disease': new_diagnostic_disease,
            'new_how_to_use': new_how_to_use,
            'new_medicine_name': new_medicine_name
        }),
        header: {
            'Content-Type': 'application/json'
        }
    })
}