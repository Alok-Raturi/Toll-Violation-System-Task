import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { jwtDecode } from 'jwt-decode';
import { ToastrService } from 'ngx-toastr';
import { tap } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private APIRoute = 'http://localhost:7071/api/';
  email: string = '';
  accessToken: string = '';

  constructor(private httpClient: HttpClient,private toast: ToastrService ) {}
  fetchVehicles() {
    return this.httpClient.get(this.APIRoute + 'user/get-vehicles', {
      headers: new HttpHeaders().set('Authorization', this.accessToken),
    });
  }

  fetchChallan(vid: string) {
    return this.httpClient.get(
      this.APIRoute + 'user/get-challans/' + vid,
      {
        headers: new HttpHeaders().set('Authorization', this.accessToken),
      }
    );
  }

  fetchFastTag() {
    return this.httpClient.get(this.APIRoute + 'user/get-fastags', {
      headers: new HttpHeaders().set('Authorization', this.accessToken),
    });
  }

  rechargeFastTag(tag_id: string, balance: number) {
    this.toast.info("Recharge payment processing......")
    return this.httpClient.post(
      this.APIRoute + 'user/recharge-fastag/' + tag_id,
      {
        amount: balance,
      },
      {
        headers: new HttpHeaders().set('Authorization', this.accessToken),
      }
    ).pipe(tap(
      {
        next:(data:any)=>{
          this.toast.success("Successfully done recharge.")
        },
        error:(err)=>{
          this.toast.error(err.error)
        }
      }
    ))
  }

  fetchHistory(tagId: string) {
    return this.httpClient.get(
      this.APIRoute + 'user/get-transaction-history/' + tagId,
      {
        headers: new HttpHeaders().set('Authorization', this.accessToken),
      }
    );
  }

  get isLoggedIn() {
    return this.email && this.accessToken;
  }

  setTokens() {
    if (typeof window !== 'undefined') {
      const accessTokenItem = JSON.parse(
        localStorage.getItem('user-tokens') as string
      );
      if (!accessTokenItem) {
        return;
      }
      const decodedJwt:{
        "email": string,
        "designation": string,
        "id": string,
        "iat": number
        "exp": number
      }= jwtDecode(accessTokenItem.accessToken);
      const now = new Date();
      if (!decodedJwt.exp) {
        localStorage.removeItem('user-tokens');
        return;
      }
      if (now.getTime() / 1000 > decodedJwt.exp) {
        localStorage.removeItem('user-tokens');
        return;
      }

      this.accessToken = accessTokenItem.accessToken;
      this.email = decodedJwt.email;
    }
  }

  decodeToken(): any {
    if (this.accessToken) {
      return jwtDecode(this.accessToken);
    }
    return null;
  }

  logout() {
    this.accessToken = this.email = '';
    localStorage.removeItem('user-tokens');
  }

  get isTokenAvailable() {
    return this.accessToken;
  }

  get userEmail() {
    return this.email;
  }

  signin(email: string, password: string) {
    return this.httpClient
      .post(this.APIRoute + 'login', {
        email,
        password,
      })
      .pipe(
        tap({
          next: (data: any) => {
            console.log("Hello")
            console.log(data)
            this.accessToken = data.access_token;
            this.email = email;
            const accessTokenItem = {
              accessToken: data.access_token,
            };
            localStorage.setItem(
              'user-tokens',
              JSON.stringify(accessTokenItem)
            );
          },
        })
      );
  }

  payAllChallan(vehicleId:string){
    this.toast.info("Paying from your associated fastag......")
    return this.httpClient.post(this.APIRoute + 'user/pay-all-challan/' + vehicleId,{},{
      headers: new HttpHeaders().set('Authorization', this.accessToken)
    }).pipe(tap(
      {
        next:(data:any)=>{
          this.toast.success("Paid challan for vehicle with vehicle id - "+vehicleId)
        },
        error:(err)=>{
          this.toast.error(err.error)
        }
      }
    ))
  }

  paySingleChallan(challanId:string){
    this.toast.info("Paying from your associated fastag......")
    return this.httpClient.post(this.APIRoute + 'user/pay-a-challan/' + challanId,{},{
      headers: new HttpHeaders().set('Authorization', this.accessToken)
    }).pipe(tap(
      {
        next:(data:any)=>{
          this.toast.success("Paid challan with challan id - "+challanId)
        },
        error:(err)=>{
          this.toast.error(err.error)
        }
      }
    ))
  }

}
