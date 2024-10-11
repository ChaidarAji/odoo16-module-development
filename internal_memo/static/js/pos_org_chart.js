var jobs = [];

odoo.define("internal_memo.position_chart", function (require) {
  "use strict";

  var AbstractAction = require("web.AbstractAction");
  var core = require("web.core");
  var QWeb = core.qweb;

  var PositionChart = AbstractAction.extend({
    template: "internal_memo.PositionChart",

    events: {
      "click .head": "_onItemClick",
      "click #create-job": "_onCreateJobClick",
    },

    init: function (parent, context) {
      this._super.apply(this, arguments);
    },

    start: function () {
      var self = this;

      this._fetchJobs().then(function () {
        self._render();
      });

      return this._super.apply(this, arguments);
    },

    _fetchJobs: function () {
      var self = this;

      return this._rpc({
        model: "master.job",
        method: "search_read",
        args: [[], ["id", "name", "parent_id", "divisi_id", "order_id"]],
      }).then(function (data) {
        jobs = data;
      });
    },

    _mapJobResponses: function (data) {
      var jobMap = {};
      
      // Initialize jobMap with jobs and empty children
      data.forEach((job) => {
        jobMap[job.id] = {
          ...job,
          children: [],
          children_num: 0 // Start with 0, to be updated later
        };
      });
    
      // Organize jobs into parent-child relationships
      var rootJobs = [];
      data.forEach((job) => {
        if (job.parent_id) {
          var parentJob = jobMap[job.parent_id[0]];
          if (parentJob) {
            parentJob.children.push(jobMap[job.id]);
          }
        } else {
          rootJobs.push(jobMap[job.id]);
        }
      });
    
      // Recursive function to count children
      function countChildren(job) {
        let count = 0;
        job.children.forEach(child => {
          count += 1 + countChildren(child); // Count each child and its descendants
        });
        job.children_num = count;
        return count;
      }
    
      // Count children for all root jobs
      rootJobs.forEach(job => countChildren(job));
    
      // Sort jobs and children by order_id
      function sortJobsByOrderId(jobs) {
        jobs.sort((a, b) => (a.order_id || 0) - (b.order_id || 0));
        jobs.forEach(job => {
          if (job.children.length > 0) {
            sortJobsByOrderId(job.children);
          }
        });
      }
      sortJobsByOrderId(rootJobs);
    
      return rootJobs;
    },
    
    
    
    _render: function () {
      var self = this;

      var org_chart = QWeb.render("internal_memo.PositionChart", {
        widget: self,
        jobs: self._mapJobResponses(jobs),
      });

      self.$el.html(org_chart);
      return org_chart;
    },

    
    // 
    // Handler
    
    _onItemClick: function (event) {
      var self = this;
      var jobId = $(event.currentTarget).data("job-id");

      this.do_action({
        type: 'ir.actions.act_window',
        res_model: 'master.job',
        res_id: jobId,
        views: [[false, 'form']],
        target: 'new',
      }, {
        on_close: function () {
          self._fetchJobs().then(function () {
            self._render();
          });
        }
      });
    },

    _onCreateJobClick: function (event) {
      var self = this;

      this.do_action({
        type: 'ir.actions.act_window',
        res_model: 'master.job',
        views: [[false, 'form']],
        target: 'new',
      }, {
        on_close: function () {
          self._fetchJobs().then(function () {
            self._render();
          });
        }
      });
    },

  });

  core.action_registry.add("position_chart", PositionChart);

  return PositionChart;
});
