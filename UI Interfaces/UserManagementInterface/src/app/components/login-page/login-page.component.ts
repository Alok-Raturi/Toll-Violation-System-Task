import { Component } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ToastrService} from 'ngx-toastr';

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './login-page.component.html',
  styleUrl: './login-page.component.css'
})
export class LoginPageComponent {


  constructor(private router: Router, private authService: AuthService,private toastr:ToastrService) {}

  loginForm = new FormGroup({
    email: new FormControl('', {
      validators: [Validators.required, Validators.email],
    }),
    password: new FormControl('', { 
      validators: [Validators.required,Validators.pattern("^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=])(?=\\S+$).{8,20}$")] 
    }),
  });

  onSubmit() {
    if(this.loginForm.status==="INVALID"){
      if (this.loginForm.controls['email'].status === 'INVALID' ){
        this.toastr.error("Email not valid.")
      }
      if(this.loginForm.controls['password'].status === "INVALID"){
        this.toastr.warning("Your password should have at least 1 uppercase characters, at least 1 special character, at least 1 digits, at least 1 lowercase characters, should not contain any whitespace characters, should have minimum length of 8 characters and max length of 20 characters")
      }
      return;
    }
    const email = this.loginForm.value.email as string;
    const password = this.loginForm.value.password as string;
    this.toastr.info("Logging you in.....")
    this.authService.signin(email,password).subscribe({
      next: (res) => {
        this.router.navigate(['dashboard']);
        this.toastr.success("Successfully logged in")
      },
      error: (err) => {
        console.log(err);
        this.toastr.error(err.error)
      },
    });
  }
}
