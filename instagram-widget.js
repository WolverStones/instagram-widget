/* 
< !--Instagram Feed Widget-- >
< !--Author: Patrik Müller-- >
< !--GitHub: https://github.com/WolverStones -->
< !--License: Apache - 2.0 -- >
< !--
   Licensed under the Apache License, Version 2.0(the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
 */

document.addEventListener("DOMContentLoaded", () => {
   const container = document.getElementById("instagram-widget");
   if (!container) return;

   container.innerHTML = `
        <div id="profile-container" style="display: flex; align-items: center; justify-content: space-between; padding: 25px; background: white; border-radius: 15px; box-shadow: 0px 4px 12px rgba(0,0,0,0.1); max-width: 1000px; margin: auto;">
            <div style="display: flex; align-items: center;">
                <div style="width: 110px; height: 110px; border-radius: 50%; background: linear-gradient(45deg, #f9ce34, #ee2a7b, #6228d7); padding: 2px; display: flex; align-items: center; justify-content: center;">
                    <img src="https://i.imgur.com/IZZQHpn.jpeg" alt="Profile Picture" style="width: 100px; height: 100px; border-radius: 50%; background: white; padding: 3px;">
                </div>
                <div style="margin-left: 20px;">
                    <h1 style="font-weight: bold; font-size: 26px; margin: 0;">Nart dance school</h1>
                    <p style="font-size: 18px; color: gray; margin: 0;">@nartdanceschool</p>
                </div>
            </div>
        </div>
        <div id="feed" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; padding: 15px; max-width: 1000px; margin: auto;"></div>
    `;

   const loadInstagramData = async () => {
      try {
         const response = await fetch('https://node.agonia.cz/instagram/feed?limit=4');
         if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
         const data = await response.json();

         document.getElementById('feed').innerHTML = '';

         for (const post of data.feed) {
            if (!post.media_url) continue;

            const postElement = document.createElement('div');
            postElement.style = "position: relative; overflow: hidden; border-radius: 8px;";

            const link = document.createElement('a');
            link.href = post.permalink;
            link.target = '_blank';

            if (post.media_type === 'VIDEO') {
               const video = document.createElement('video');
               Object.assign(video, { src: post.media_url, width: "100%", height: "100%", muted: true, loop: true, autoplay: true, style: "object-fit: cover; pointer-events: none;" });

               const playIcon = document.createElement('div');
               Object.assign(playIcon.style, { position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', background: 'rgba(0, 0, 0, 0.5)', color: 'white', fontSize: '40px', padding: '10px 15px', borderRadius: '50%', cursor: 'pointer' });
               playIcon.textContent = '▶';

               link.append(video, playIcon);
               postElement.append(link);
            } else {
               const img = document.createElement('img');
               Object.assign(img, { src: post.media_url, alt: "Instagram Post", style: "width: 100%; height: 100%; object-fit: cover;" });
               link.append(img);
               postElement.append(link);
            }

            document.getElementById('feed').append(postElement);
         }
      } catch (error) {
         console.error('Error loading feed:', error);
      }
   };

   loadInstagramData();
});
