/**
 * Copyright 2018 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
 
module "instance_template" {
  //https://registry.terraform.io/modules/terraform-google-modules/vm/google/2.1.0/submodules/instance_template
  source          = "terraform-google-modules/vm/google//modules/instance_template"
  region          = var.region
  project_id      = var.project_id
  subnetwork      = var.subnetwork
  service_account = var.service_account
  startup_script  = file("files/startup")
  
  source_image         = "debian-9-stretch-v20200309"
  source_image_family  = "debian-9"
  source_image_project = "debian-cloud" 
}

module "compute_instance" {
  source          = "terraform-google-modules/vm/google//modules/compute_instance"
  region            = var.region
  subnetwork        = var.subnetwork
  num_instances     = 1
  hostname          = "flask-server"
  instance_template = module.instance_template.self_link
}
