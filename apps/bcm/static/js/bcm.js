const app = {}

let init = (app) => {
  app.data = {
    //
    bcm_home_url: "/bcm/index",
    bcm_devices_url: "/bcm/devices",
    bcm_results_url: "/bcm/results",
    devices: [],
    device: null,
    devices_by_role: null,
    device_roles: null,
    device_role: null,
    select_device: null,
    select_role: null,
  }
  
  app.bcm_get_devices = function() {
    // Get devices in response to page load
    const url = "/bcm/get_devices"
    axios.get(url).then(function(response) {
      app.vue.devices = response.data.devices
    })
  }

  app.bcm_get_device_roles = function() {
    // Get device_roles in response to page load
    const url = "/bcm/get_device_roles"
    axios.get(url).then(function(response) {
      app.vue.device_roles = response.data.roles
    })
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

  app.bcm_select_device_role = function(event) {
    const role = event.target.value
    if (role !== 'ALL') {
      app.vue.devices_by_role = app.vue.devices.  
        filter(device => device.device_roles.includes(role))
    } else {
      app.vue.devices_by_role = app.vue.devices
    }
      app.vue.device = null
  }

  app.bcm_selected_device = function(event) {
    const device_id = parseInt(event.target.value)
    app.vue.device = app.vue.devices_by_role.find(({ id }) => id === device_id)
  }

  app.bcm_device_results_url = function(id=None) {
    if (id) {
      return `${app.vue.bcm_devices_url}/${id}/results`
    } else {
      return app.vue.bcm_devices_url
    }
  }

  app.methods = {
    button_run_cmds: app.bcm_button_run_cmds,
    button_run_cmds_role: app.bcm_button_run_cmds_role,
    bcm_device_results_url: app.bcm_device_results_url,
    select_device_role: app.bcm_select_device_role,
    selected_device: app.bcm_selected_device,
  }

  app.vue = new Vue({
    el: "#vue-target",
    data: app.data,
    methods: app.methods
  })

  app.init = () => {
    //load the devices...
    app.bcm_get_devices()
    app.bcm_get_device_roles()
  }
  
  app.init()
}

init(app)
