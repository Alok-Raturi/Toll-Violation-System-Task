import { HttpClient, HttpHeaders } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { jwtDecode } from "jwt-decode";
import { tap } from "rxjs";

@Injectable({
    providedIn: 'root'
})
export class AuthService{
    private APIRoute = "https://feb-ringtone-printing-steam.trycloudflare.com/api/user";
    private userDetails:{
        email:string,
        accessToken:string
    } = {email:"",accessToken:""};
    constructor(private httpClient: HttpClient){}

    login(email: string, password: string) {
        return this.httpClient.post(this.APIRoute+"/login",{
            email: email,
            password: password
        }).pipe(
            tap((respData:any)=>{
                this.userDetails = {
                    email: email,
                    accessToken: respData.access_token,
                };
                let decoded = jwtDecode(respData.access_token);
                console.log(decoded);
                this.handleAuth(respData.access_token);
            }),
        );
    }

    fetchVehicles() {
        return this.httpClient.get(this.APIRoute+"/get-vehicles",
            {
                headers:new HttpHeaders().set("Authorization",this.userDetails.accessToken)
            }
        )
    }

    fetchChallan(vid:string) {
        return this.httpClient.get(this.APIRoute+"/get-challan-by-vehicles/"+vid,
            {
                headers:new HttpHeaders().set("Authorization",this.userDetails.accessToken)
            }
        )
    }

    fetchFastTag() {
        return this.httpClient.get(this.APIRoute+"/get-fastags",{
            headers: new HttpHeaders().set("Authorization",this.userDetails.accessToken)
        })
    }

    rechargeFastTag(tag_id: string, balance: string) {
        return this.httpClient.post(this.APIRoute+"/recharge-fastag/"+tag_id,{
            amount:balance
        },{
            headers: new HttpHeaders().set("Authorization",this.userDetails.accessToken)
        });
    }

    fetchHistory(tagId:string) {
        return this.httpClient.get(this.APIRoute+"/get-transaction-history/"+tagId,
            {
                headers: new HttpHeaders().set("Authorization",this.userDetails.accessToken)
            });
    }

    handleAuth(accessToken: string) {
        localStorage.setItem('userAccessToken',JSON.stringify(accessToken));
    }

    autoLogin() {
        let accessToken = JSON.parse(localStorage.getItem('userAccessToken') as string);
        if (!accessToken){
            return;
        }
        else {
            let decodedData:any = jwtDecode(accessToken);
            this.userDetails.accessToken=accessToken;
            this.userDetails.email = decodedData.email;

        }
    }

    expChecker(accessToken:string) {
        let decodedExp =  (jwtDecode(accessToken).exp as number);
        let now = (new Date()).getTime();
        if (!decodedExp) {
            return false;
        } else {
            if (decodedExp>now) {
                return true;
            } else {
                return false;
            }
        }
    }

    get isTokenAvailable() {
        return this.userDetails.accessToken ;
      }
    get userEmail() {
        return this.userDetails.email;
    }
}