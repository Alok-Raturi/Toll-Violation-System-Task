import { Component, Input } from '@angular/core';
import { AuthService } from '../shared/auth.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [],
  templateUrl: './header.component.html',
  styleUrl: './header.component.css'
})
export class HeaderComponent {
  uName = "";
  constructor(private authService: AuthService) {}

  ngOnInit() {
    this.uName = this.authService.userEmail;
  }

}
