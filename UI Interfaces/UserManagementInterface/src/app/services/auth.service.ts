import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { jwtDecode } from 'jwt-decode';
import { tap } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private APIRoute = 'http://localhost:7071/api/user/';
  email: string = '';
  accessToken: string = '';

  constructor(private httpClient: HttpClient ) {}
  fetchVehicles() {
    return this.httpClient.get(this.APIRoute + 'get-vehicles', {
      headers: new HttpHeaders().set('Authorization', this.accessToken),
    });
  }

  fetchChallan(vid: string) {
    return this.httpClient.get(
      this.APIRoute + 'get-challan-by-vehicles/' + vid,
      {
        headers: new HttpHeaders().set('Authorization', this.accessToken),
      }
    );
  }

  fetchFastTag() {
    return this.httpClient.get(this.APIRoute + 'get-fastags', {
      headers: new HttpHeaders().set('Authorization', this.accessToken),
    });
  }

  rechargeFastTag(tag_id: string, balance: number) {
    return this.httpClient.post(
      this.APIRoute + 'recharge-fastag/' + tag_id,
      {
        amount: balance,
      },
      {
        headers: new HttpHeaders().set('Authorization', this.accessToken),
      }
    )
  }

  fetchHistory(tagId: string) {
    return this.httpClient.get(
      this.APIRoute + 'get-transaction-history/' + tagId,
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
    return this.httpClient.post(this.APIRoute + 'pay-all-challan/' + vehicleId,{
      headers: new HttpHeaders().set('Authorization', this.accessToken)
    })
  }

  paySingleChallan(challanId:string){
    return this.httpClient.post(this.APIRoute + 'pay-a-challan/' + challanId,{
      headers: new HttpHeaders().set('Authorization', this.accessToken)
    })
  }

}
