<template>
  <div>
    <h2 class="mb-4">Configuration</h2>
    <p class="text-muted mb-4">Manage system settings, connections, and sync rules.</p>

    <div class="accordion" id="configAccordion">
      <div class="accordion-item">
        <h2 class="accordion-header" id="headingConnections">
          <button
            class="accordion-button"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#collapseConnections"
            aria-expanded="true"
            aria-controls="collapseConnections"
          >
            <i class="fas fa-database me-2"></i> Connection Settings
          </button>
        </h2>
        <div
          id="collapseConnections"
          class="accordion-collapse collapse show"
          aria-labelledby="headingConnections"
          data-bs-parent="#configAccordion"
        >
          <div class="accordion-body">
            <h5 class="mb-3">MySQL Connection</h5>
            <form>
              <div class="mb-3 row">
                <label for="mysqlHost" class="col-sm-3 col-form-label">Host</label>
                <div class="col-sm-9">
                  <input type="text" class="form-control" id="mysqlHost" value="mysql.nakuru.local" />
                </div>
              </div>
              <div class="mb-3 row">
                <label for="mysqlUser" class="col-sm-3 col-form-label">Username</label>
                <div class="col-sm-9"><input type="text" class="form-control" id="mysqlUser" value="sync_user" /></div>
              </div>
              <div class="mb-3 row">
                <label for="mysqlPass" class="col-sm-3 col-form-label">Password</label>
                <div class="col-sm-9">
                  <input type="password" class="form-control" id="mysqlPass" value="************" />
                </div>
              </div>
              <button type="button" class="btn btn-sm btn-outline-secondary me-2">Test Connection</button>
              <button type="submit" class="btn btn-sm btn-primary">Save MySQL Settings</button>
            </form>
            <hr class="my-4" />
            <h5 class="mb-3">Freshworks CRM Connection</h5>
            <form>
              <div class="mb-3 row">
                <label for="fwDomain" class="col-sm-3 col-form-label">Domain</label>
                <div class="col-sm-9">
                  <input type="text" class="form-control" id="fwDomain" value="nakuru-crm.freshworks.com" />
                </div>
              </div>
              <div class="mb-3 row">
                <label for="fwApiKey" class="col-sm-3 col-form-label">API Key</label>
                <div class="col-sm-9">
                  <input type="password" class="form-control" id="fwApiKey" value="************" />
                </div>
              </div>
              <button type="button" class="btn btn-sm btn-outline-secondary me-2">Test Connection</button>
              <button type="submit" class="btn btn-sm btn-primary">Save Freshworks Settings</button>
            </form>
          </div>
        </div>
      </div>

      <div class="accordion-item">
        <h2 class="accordion-header" id="headingRules">
          <button
            class="accordion-button collapsed"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#collapseRules"
            aria-expanded="false"
            aria-controls="collapseRules"
          >
            <i class="fas fa-cogs me-2"></i> Sync Rules & Scheduling
          </button>
        </h2>
        <div
          id="collapseRules"
          class="accordion-collapse collapse"
          aria-labelledby="headingRules"
          data-bs-parent="#configAccordion"
        >
          <div class="accordion-body">
            <p class="text-muted">Configure which objects/fields to sync and how often.</p>
            <div class="alert alert-secondary">Sync rule configuration interface placeholder...</div>

            <h5 class="mt-4">Scheduling</h5>
            <form>
              <div class="form-check form-switch mb-2">
                <input class="form-check-input" type="checkbox" role="switch" id="enableTwoWaySchedule" checked />
                <label class="form-check-label" for="enableTwoWaySchedule">Enable Scheduled Two-Way Sync</label>
              </div>
              <label for="twoWayFrequency" class="form-label small">Frequency</label>
              <select id="twoWayFrequency" class="form-select form-select-sm mb-3" style="max-width: 200px">
                <option>Every 15 Minutes</option>
                <option selected>Every Hour</option>
                <option>Every 4 Hours</option>
                <option>Daily</option>
              </select>

              <div class="form-check form-switch mb-2">
                <input class="form-check-input" type="checkbox" role="switch" id="enableBulkSchedule" />
                <label class="form-check-label" for="enableBulkSchedule">Enable Scheduled Bulk Upload</label>
              </div>
              <label for="bulkScheduleTime" class="form-label small">Time (EAT)</label>
              <input
                type="time"
                id="bulkScheduleTime"
                class="form-control form-control-sm"
                value="02:00"
                style="max-width: 150px"
              />

              <button type="submit" class="btn btn-sm btn-primary mt-3">Save Schedule Settings</button>
            </form>
          </div>
        </div>
      </div>

      <div class="accordion-item">
        <h2 class="accordion-header" id="headingNotifications">
          <button
            class="accordion-button collapsed"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#collapseNotifications"
            aria-expanded="false"
            aria-controls="collapseNotifications"
          >
            <i class="fas fa-bell me-2"></i> Notification Settings
          </button>
        </h2>
        <div
          id="collapseNotifications"
          class="accordion-collapse collapse"
          aria-labelledby="headingNotifications"
          data-bs-parent="#configAccordion"
        >
          <div class="accordion-body">
            <p class="text-muted">Configure email alerts for sync events.</p>
            <form>
              <div class="mb-3">
                <label for="notifyEmails" class="form-label">Send alerts to (comma-separated):</label>
                <input
                  type="email"
                  multiple
                  class="form-control"
                  id="notifyEmails"
                  placeholder="admin@example.com, support@example.com"
                  value="admin@nakuru-SME Doc Generator.co.ke"
                />
              </div>
              <label class="form-label">Notify on:</label>
              <div class="form-check">
                <input class="form-check-input" type="checkbox" value="" id="notifyFailure" checked />
                <label class="form-check-label" for="notifyFailure">Sync Failure / Error</label>
              </div>
              <div class="form-check">
                <input class="form-check-input" type="checkbox" value="" id="notifySuccessErrors" />
                <label class="form-check-label" for="notifySuccessErrors">Sync Success with Errors</label>
              </div>
              <div class="form-check">
                <input class="form-check-input" type="checkbox" value="" id="notifyConfigChange" />
                <label class="form-check-label" for="notifyConfigChange">Configuration Changes</label>
              </div>
              <button type="submit" class="btn btn-sm btn-primary mt-3">Save Notification Settings</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfigurationView',
  // Add data/methods for handling form submissions if needed
}
</script>
