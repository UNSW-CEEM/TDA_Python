console.log('Hi, the menu js loaded')
//For example we are defining menu in object. You can also define it on Ul list. See on documentation.
var menu = [{
        name: 'create',
        title: 'create button',
        fun: function () {
            alert('i am add button')
        }
    }, {
        name: 'update',
        title: 'update button',
        fun: function () {
            alert('i am update button')
        }
    }, {
        name: 'delete',
        title: 'delete button',
        fun: function () {
            alert('i am delete button')
        }
    }];

//Calling context menu
$('#projectmenu').contextMenu(menu, {displayAround: 'trigger', verAdjust:24, horAdjust:-55});