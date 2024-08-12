// keeping so i don't have to rewrite this code later, even though it's not being used right now
// document.addEventListener('DOMContentLoaded', function() {
//     console.log('DOM loaded with JavaScript');

//     var elem = document.querySelector('.gallery');
//     var pageIndex = 1;
//     var perPage = 10;

//     function loadPhotos() {
//         fetch(`/api/photos?page=${pageIndex}&per_page=${perPage}`)
//             .then(response => response.json())
//             .then(data => {
//                 console.log('Fetched data:', data);
//                 var photos = data.photos;
//                 var itemsHTML = photos.map(function(photo) {
//                     return `<div class="photo">
//                                 <img src="${photo.url}" alt="${photo.title}">
//                                 <p>${photo.title}</p>
//                             </div>`;
//                 }).join('');
//                 var proxyElem = document.createElement('div');
//                 proxyElem.innerHTML = itemsHTML;
//                 var items = proxyElem.querySelectorAll('.photo');
//                 elem.append(...items);
//                 pageIndex++;
//                 if (!data.has_more) {
//                     infScroll.destroy();  // Stop Infinite Scroll if there are no more pages
//                 }
//             })
//             .catch(error => console.error('Fetch error:', error));
//     }

//     var infScroll = new InfiniteScroll(elem, {
//         path: function() {
//             return `/api/photos?page=${pageIndex}&per_page=${perPage}`;
//         },
//         append: false, // We'll handle appending manually
//         history: false,
//         scrollThreshold: 400,
//     });

//     infScroll.on('scrollThreshold', loadPhotos);  // Trigger loadPhotos on scroll
//     loadPhotos();  // Initial load

//     console.log('InfiniteScroll initialized and manual fetching setup');
// });