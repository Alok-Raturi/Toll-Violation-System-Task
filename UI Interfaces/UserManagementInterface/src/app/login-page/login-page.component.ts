import { Component } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../shared/auth.service';

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './login-page.component.html',
  styleUrl: './login-page.component.css'
})
export class LoginPageComponent {


  constructor(private router: Router, private authService: AuthService) {}

  loginForm = new FormGroup({
    email: new FormControl('', {
      validators: [Validators.required, Validators.email],
    }),
    password: new FormControl('', { validators: [Validators.required] }),
  });

  onSubmit() {
    const email = this.loginForm.value.email;
    const password = this.loginForm.value.password;
    this.authService.login(email!,password!).subscribe(
      (respData) => {
        console.log(respData);
        this.router.navigate(['dashboard']);
      },
      (errorMessage) => {
        alert(errorMessage);
      }
    );
    // this.router.navigate(['dashboard']);
  }
}
