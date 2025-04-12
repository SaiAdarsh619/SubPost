async function login(event) {
    event.preventDefault();
    document.getElementById('submit').addAttribute('disabled');
    // Get the form data
    const loginform = document.getElementById('loginform');
    const formdata = new FormData(loginform);
    const jsondata = Object.fromEntries(formdata.entries());
    console.log(jsondata);

    const port = 5000;
    const domain = "domainc.ddns.net"
    const domainon = true
    const url = domainon ? `http://${domain}:${port}/login` : `http://localhost:5000/login`;
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(jsondata)
    }).then(response =>{
        // if response contains redirection info
        if(response.redirected)
        {
            //redirect their
            window.location.href = response.url;
        }
    }
    ).catch(error => console.error("Error : ",error));
    
    if(response.ok)
        console.log('login successfull');
    else
    console.log('login failed');
}