import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import {  HttpClientModule } from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { DropComponent } from './drop/drop.component';
import { NgxDropzoneModule } from 'ngx-dropzone';
import { MatCardModule } from '@angular/material/card';
import { FormsModule } from '@angular/forms';

import { FormsComponent } from './forms/forms.component';

@NgModule({
  declarations: [
    AppComponent,
    DropComponent,
    FormsComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    NgxDropzoneModule,
    MatCardModule,FormsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
