import { Component } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [RouterLink,RouterLinkActive],
  templateUrl: './header.component.html',
  styleUrl: './header.component.css'
})
export class HeaderComponent {
  email = "";
  constructor(private authService: AuthService,private router:Router) {}

  ngOnInit() {
    this.email = this.authService.userEmail
  }

  logout(){
    this.authService.logout()
    this.router.navigate(['login'])
  }

}
