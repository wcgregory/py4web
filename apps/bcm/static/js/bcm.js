const app = {}

let init = (app) => {
  app.data = {
    //
    devices: [],
    selectedOption: null,
    select_device: null
  }
  
  app.bcm_button_run_cmds = function(device_id) {
    console.log("Test - Button Pressed")
    let url="/bcm/run_commands/" + device_id
    axios.get(url).then(function(response) {
      console.log(response.data)
    })
  }

  app.bcm_button_run_cmds_role = function(device_role) {
    console.log("Test - Button Pressed")
    let url="/bcm/run_commands_by_role/" + device_role
    axios.get(url).then(function(response) {
      console.log(response.data)
    })
  }

  app.get_devices = function() {
    // Get devices in response to page load
    const url = "/bcm/get_devices"
    axios.get(url).then(function(response) {
      app.vue.devices = response.data.devices
    })
  }

  app.selected_device = function() {
    //const url = "bcm/devices/<device_id:int>"
    //this.device = this.devices
    console.log("Test - Selected Device ", this.select_device)
  }

  app.methods = {
    bcm_button_run_cmds: app.bcm_button_run_cmds,
    bcm_button_run_cmds_role: app.bcm_button_run_cmds_role,
    selected_device: app.selected_device,
    logSelectedOption() {
      console.log('Selected Option:', this.selectedOption)
    }
  }

  app.vue = new Vue({
    el: "#vue-target",
    data: app.data,
    methods: app.methods
  })

  app.init = () => {
    //load the devices...
    app.get_devices()
  }
  
  app.init()
}

init(app)
