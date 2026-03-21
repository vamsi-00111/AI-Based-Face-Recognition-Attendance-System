let detectInterval = null
let cameraRunning = false


// START CAMERA
async function startCamera(){

    const video = document.getElementById("video")
    const canvas = document.getElementById("canvas")

    cameraRunning = true

    try{

        const stream = await navigator.mediaDevices.getUserMedia({
            video:{
                width:640,
                height:480
            }
        })

        video.srcObject = stream

        video.onloadedmetadata = () => {

            canvas.width = 640
            canvas.height = 480

        }

        document.getElementById("detected").innerText = "Camera started..."

        if(!detectInterval){
            detectLoop()
        }

    }catch(error){

        alert("Camera permission denied")

    }

}


// STOP CAMERA
function stopCamera(){

    const video = document.getElementById("video")
    const canvas = document.getElementById("canvas")
    const ctx = canvas.getContext("2d")

    cameraRunning = false

    // stop detection loop
    if(detectInterval){
        clearInterval(detectInterval)
        detectInterval = null
    }

    // stop camera stream
    if(video.srcObject){
        video.srcObject.getTracks().forEach(track => track.stop())
        video.srcObject = null
    }

    // clear video
    video.pause()
    video.srcObject = null

    // clear canvas completely
    ctx.clearRect(0,0,canvas.width,canvas.height)

    // reset canvas by resizing (guaranteed clear)
    canvas.width = canvas.width

    document.getElementById("detected").innerText = "Camera stopped"
}


// FACE DETECTION LOOP
function detectLoop(){

    const video = document.getElementById("video")
    const canvas = document.getElementById("canvas")
    const ctx = canvas.getContext("2d")

    detectInterval = setInterval(async ()=>{

        if(!cameraRunning){
            ctx.clearRect(0,0,canvas.width,canvas.height)
            return
        }

        ctx.drawImage(video,0,0,canvas.width,canvas.height)

        canvas.toBlob(async function(blob){

            if(!cameraRunning){
                return
            }

            let formData = new FormData()
            formData.append("file",blob,"frame.jpg")

            try{

                let response = await fetch("http://127.0.0.1:8000/detect",{
                    method:"POST",
                    body:formData
                })

                let data = await response.json()

                ctx.drawImage(video,0,0,canvas.width,canvas.height)

                if(data.detected_faces && data.detected_faces.length > 0){

                    let names = []

                    data.detected_faces.forEach(face => {

                        let left = face.left
                        let top = face.top
                        let right = face.right
                        let bottom = face.bottom

                        let width = right - left
                        let height = bottom - top

                        ctx.strokeStyle = "lime"
                        ctx.lineWidth = 3
                        ctx.strokeRect(left,top,width,height)

                        ctx.fillStyle = "lime"
                        ctx.font = "16px Arial"
                        ctx.fillText(face.name,left,top-8)

                        names.push(face.name)

                    })

                    document.getElementById("detected").innerText =
                        "Detected: " + names.join(", ")

                }else{

                    document.getElementById("detected").innerText =
                        "No face detected"

                }

            }catch(error){

                document.getElementById("detected").innerText =
                    "Server error"

            }

        },"image/jpeg")

    },600)

}
async function getAttendance(){

    let date = document.getElementById("date").value

    if(!date){
        alert("Please select a date")
        return
    }

    let response = await fetch(`http://127.0.0.1:8000/attendance/date/${date}`)
    let data = await response.json()

    let resultDiv = document.getElementById("attendance_result")

    resultDiv.innerHTML = ""

    if(data.records.length === 0){

        resultDiv.innerHTML = "<p>No attendance records found</p>"
        return
    }

    data.records.forEach(student => {

        resultDiv.innerHTML += `
        <p>
        ${student.student_id} - ${student.name} - ${student.time}
        </p>
        `
    })

}

async function totalAttendance(){

    let id = document.getElementById("student_search").value

    if(!id){
        alert("Enter Student ID")
        return
    }

    let response = await fetch(`http://127.0.0.1:8000/attendance/student/${id}`)
    let data = await response.json()

    document.getElementById("total_result").innerHTML =
        `Total Present Days: ${data.total_present}`
}

async function register(){

    const studentId = document.getElementById("student_id").value
    const name = document.getElementById("name").value
    const imageFile = document.getElementById("image").files[0]

    if(!studentId || !name || !imageFile){
        alert("Please enter ID, name and select an image")
        return
    }

    let formData = new FormData()

    formData.append("student_id", studentId)
    formData.append("name", name)
    formData.append("file", imageFile)

    try{

        let response = await fetch("http://127.0.0.1:8000/register",{
            method:"POST",
            body:formData
        })

        let result = await response.json()

        console.log(result)

        alert(result.message)

    }catch(error){

        console.log(error)
        alert("Registration failed")

    }

}