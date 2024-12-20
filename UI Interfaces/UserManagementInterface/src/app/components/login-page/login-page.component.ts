import { Component } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

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
    const email = this.loginForm.value.email as string;
    const password = this.loginForm.value.password as string;
    this.authService.signin(email,password).subscribe({
      next: (res) => {
        console.log(res);
        this.router.navigate(['dashboard']);
      },
      error: (err) => {
        console.log(err);
      },
    });
    // this.router.navigate(['dashboard']);
  }
}
