var textListResource = Vue.resource(
    TEXT_LIST_RESOURCE_URI,
    {},
    {},
    {
        headers: {'X-CSRFToken': CSRF_TOKEN}
    }
);


var mediator = new Vue({
    created: function() {
        this.$on('textAdded', function(response) {
            textListVM.updateFromPageNum(1);
            notificationVM.show(
                (
                    'Text #' + response.body['id']
                    + ' created at ' + response.body['created_at']
                ),
                'success'
            );
        });
        this.$on('textNotAdded', function (response) {
            notificationVM.show(response.body, 'error');
        });

        this.$on('textListUpdated', function (response) {});
        this.$on('textListNotUpdated', function (response) {
            notificationVM.show(response.body, 'error');
        })
    }
});


const NOTIFICATION_TYPES_CLASSES_MAPPING = {
    'error': 'error',
    'success': 'success'
};
const NOTIFICATION_SHOWING_DURATION_MS = 5000;


var notificationVM = new Vue({
    el: '#notification',
    data: {
        message: '',
        type: '',
    },
    methods: {
        show: function (message, type) {
            this.message = message;
            this.type = type;
            setTimeout(this.hide, NOTIFICATION_SHOWING_DURATION_MS);
        },
        hide: function () {
            this.message = '';
            this.type = '';
        }
    }
});


var textListVM = new Vue({
    el: '#text_list',
    data: {
        texts: [],
        previous_page_num: null,
        next_page_num: null
    },
    created: function() {
        // Отображаем первую страницу при загрузке списка
        this.updateFromPageNum(1);
    },
    methods: {
        updateFromPageNum: function (pageNum) {
            textListResource.get({page: pageNum}).then(
                response => {
                    this.texts = response.body['results'];
                    this.previous_page_num = response.body['previous'];
                    this.next_page_num = response.body['next'];
                    mediator.$emit('textListUpdated', response);
                },
                response => {
                    mediator.$emit('textListNotUpdated', response);
                }
            );
        }
    }
});



var addTextFormVM = new Vue({
    el: '#add_text_form',
    data: {
        content: ''
    },
    methods: {
        add_text: function () {
            textListResource.save({}, {'content': content.value}).then(
                response => {
                    content.value = '';
                    mediator.$emit('textAdded', response);
                },
                response => {
                    mediator.$emit('textNotAdded', response)
                }
            );
        }
    }
});
