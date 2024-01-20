
currentPageURL = window.location.href;
pageContent = document.documentElement.innerHTML;
links = []
controlledUrls = []
const pendingLinks = new Set();
const paintedLinks =  new Map();

function reloadPageContent(){
  this.pageContent = document.documentElement.innerHTML;
  getLinks();
}

document.addEventListener("readystatechange", function() {
  if (document.readyState === "interactive" || document.readyState === "complete") {
    getLinks();
    observePageChanges();
  }
});

function observePageChanges() {
  const observer = new MutationObserver(function(mutationsList) {
    for (let mutation of mutationsList) {
      if (mutation.type === 'childList' || mutation.type === 'subtree') {
        if(mutation.addedNodes){
          Array.from(mutation.addedNodes).forEach(html =>{
            if(html.nodeName == "DIV"){
              if(html.innerHTML.includes('a')){
                reloadPageContent()
              }
            }
          })
        }
        break;
      }
    }
  });

  observer.observe(document.body, { 
    childList: true, 
    subtree: true 
  });
}

  observer.observe(document.body, { 
    childList: true, 
    subtree: true 
  });
  
  function paintLinks() {
    const allLinks = document.querySelectorAll('a');
    allLinks.forEach(link => {
      const url = link.href;
      const controlledUrl = controlledUrls.find(item => url.includes(item.url));
  
      if (!paintedLinks.has(link)) {
        let marker = '';
  
        if (controlledUrl) {
          switch (controlledUrl.zone) {
            case 'Red':
              marker = ' ⛔';
              link.addEventListener('click', handleLinkClick);
              link.setAttribute('title', 'Dangerous');
              break;
            case 'Green':
              marker = ' ✅';
              link.setAttribute('title', 'Trusted');
              break;
            case 'Yellow':
              marker = ' ⚠️';
              link.addEventListener('click', handleLinkClick);
              link.setAttribute('title', 'Adware and other');
              break;
            case 'Orange':
              marker = ' 🔶';
              link.addEventListener('click', handleLinkClick);
              link.setAttribute('title', 'Not trusted');
              break;
            case 'Grey':
              marker = ' ❔';
              link.setAttribute('title', 'No data');
              break;
            default:
              marker = ' ⏳';
              link.setAttribute('title', 'Pending');
              break;
          }
        } else {
          marker = ' ⏳';
          link.setAttribute('title', 'Pending');
        }
  
        paintedLinks.set(link, marker);
  
        const markerSpan = document.createElement('span');
        markerSpan.textContent = marker;
        link.appendChild(markerSpan);
      } else {
        const existingMarker = paintedLinks.get(link);
        if (existingMarker === ' ⏳' && controlledUrl) {
          link.removeChild(link.lastChild);
          let newMarker = '';
          let newTitle = '';
          switch (controlledUrl.zone) {
            case 'Red':
              newMarker = ' ⛔';
              link.addEventListener('click', handleLinkClick);
              newTitle = 'Dangerous';
              break;
            case 'Green':
              newMarker = ' ✅';
              newTitle = 'Trusted';
              break;
            case 'Yellow':
              newMarker = ' ⚠️';
              link.addEventListener('click', handleLinkClick);
              newTitle = 'Adware and other';
              break;
            case 'Orange':
              newMarker = ' 🔶';
              link.addEventListener('click', handleLinkClick);
              newTitle = 'Not trusted';
              break;
            case 'Grey':
              newMarker = ' ❔';
              newTitle = 'No data';
              break;
            default:
              newMarker = ' ⏳';
              newTitle = 'Pending';
              break;
          }
          paintedLinks.set(link, newMarker);
  
          const newMarkerSpan = document.createElement('span');
          newMarkerSpan.textContent = newMarker;
          link.appendChild(newMarkerSpan);
  
          if (newTitle !== '') {
            link.setAttribute('title', newTitle);
          }
        }
      }
    });
  }
  
  
  
  

  function handleLinkClick(event) {
    event.preventDefault();
    const link = event.currentTarget;
    const confirmation = confirm("Bağlantı tehlikeli gözüküyor, gitmek istediğinize emin misiniz?");
  
    if (confirmation) {
      window.location.href = link.href;
      link.removeEventListener('click', handleLinkClick);
    }
  }
  
 async function getLinks() {
  this.paintLinks()
  await fetch('http://127.0.0.1:8000/get-links', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ 
      content: pageContent,
      url: currentPageURL
    }),
  })
    .then(response => {
      if (response.ok) {
        return response.json();
      }
      throw new Error('Linkler ayrıştırılamadı.');
    })
    .then(async data => {
      checkLinksAsync(data).then((results) => {
        this.links=data
      });

    })
    .catch(error => {
      console.error('Hata:', error);
    });
 }

 async function checkLinksAsync(newData) {
  try {
    const promises = newData.map(async (element) => {
      if(!this.links.includes(element) && element){
        const response = await fetch('http://127.0.0.1:8000/link-control', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            url: element
          })
        })
  
        if (response.ok) {
          const controlledUrl = await response.json();
          this.controlledUrls.push(controlledUrl)
          this.paintLinks()
          return controlledUrl;
        } else {
          throw new Error('Linkler kontrol edilemedi.');
        }
      }
    });

    const results = await Promise.all(promises);
    return results;
  } catch (error) {
    console.error(error);
    return [];
  }


}
