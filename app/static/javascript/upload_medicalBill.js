//function add_new_medicalBill(new_customer_name, new_phoneNumber, new_age, new_gender,
//            new_maPhieuKham, new_symptom, new_diagnostic_disease, new_how_to_use, new_medicine_name) {
//
//    event.preventDefault();
//
//    fetch('/api/new-regulation', {
//        method: 'post',
//        body: JSON.stringify({
//            'new_customer_name': new_customer_name,
//            'new_phoneNumber': new_phoneNumber,
//            'new_age': new_age,
//            'new_gender': new_gender,
//            'new_maPhieuKham': new_maPhieuKham,
//            'new_symptom': new_symptom,
//            'new_diagnostic_disease': new_diagnostic_disease,
//            'new_how_to_use': new_how_to_use,
//            'new_medicine_name': new_medicine_name
//        }),
//        header: {
//            'Content-Type': 'application/json'
//        }
//    })
//}

function loadPatient(obj){
    fetch('/admin/createmedicalbill',{
        method:'post',
        body:JSON.stringify({
            'sdt':obj.value
        }),
        headers:{
        'Content-Type': 'application/json'
        }
    }).then(res => res.json()).then(data =>{
        if (data.status == 201){
            let p = data.patient
            let area = document.getElementById('patient-info')

            area.innerHTML = `
            <div class="row d-flex">
                <div class="form-group p-2 flex-fill d-flex" style="margin-bottom:0rem">
                    <label for="customer_name" class="p-2 flex-fill col-md-3">Tên khách hàng:</label>
                    <input style="" value="${p.first_name}" name="customer_name"  type="text" class="form-control p-2 flex-fill" placeholder="Nhập tên khách hàng" required id="customer_name">
                </div>
                <div class="form-group p-2 flex-fill d-flex" style="margin-bottom:0rem">
                    <label for="phoneNumber" class="p-2 flex-fill col-md-3">Số điện thoại:</label>
                    <input onblur="loadPatient(this)" value="${p.phone_number}" style="margin-right:0.5rem" name="phoneNumber" type="text" class="form-control p-2 flex-fill" placeholder="Nhập số điện thoại" required id="phoneNumber">
                </div>
            </div>
            <div class="row d-flex">
                <div class="p-2 d-flex col-md-4">
                    <label class="p-2">Tuổi</label>
                    <span class="text-success p-2" style="margin-left:1rem; margin-right:1rem">${p.age}</span>
                </div>
                <div class="p-2 d-flex col-md-4">
                    <label class="p-2">Giới tính</label>
                    <span class="text-info p-2" style="margin-left:1rem; margin-right:1rem">${p.gender}</span>
                </div>
                <div class="p-2 d-flex col-md-4">
                    <label class="p-2">Mã phiếu</label>
                    <span class="text-danger p-2" style="margin-left:1rem; margin-right:1rem">1234</span>
                </div>
            </div>
            `
        } else if(data.status == 404){
            alert(data.err_msg)
        }
    })
}