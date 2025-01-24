const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Lighting
const light = new THREE.AmbientLight(0xffffff, 0.8);
scene.add(light);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 10, 7.5).normalize();
scene.add(directionalLight);

camera.position.z = 5;
// Import OrbitControls
const controls = new THREE.OrbitControls(camera, renderer.domElement);

// Set control options (optional)
controls.enableDamping = true; // Smooth transitions
controls.dampingFactor = 0.05; // Damping inertia
controls.screenSpacePanning = false; // Disable panning in screen space
controls.minDistance = 1; // Minimum zoom distance
controls.maxDistance = 20; // Maximum zoom distance

// Update controls in the animation loop


const animate = () => {
    requestAnimationFrame(animate);
    controls.update(); // Required for damping
    renderer.render(scene, camera);
};



const fileInput = document.getElementById('file-input');
const loader = new THREE.STLLoader();

fileInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const geometry = loader.parse(e.target.result);

            // Create the mesh
            const material = new THREE.MeshStandardMaterial({ color: 0x606060 });
            const mesh = new THREE.Mesh(geometry, material);
            scene.add(mesh);

            // Compute the bounding box
            geometry.computeBoundingBox();
            const boundingBox = geometry.boundingBox;

            // Calculate the center of the bounding box
            const center = new THREE.Vector3();
            boundingBox.getCenter(center);

            // Re-center the geometry around the origin
            mesh.geometry.translate(-center.x, -center.y, -center.z);

            // Update the OrbitControls target
            controls.target.copy(center);
            controls.update();
        };
        reader.readAsArrayBuffer(file);
    }
});

window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

animate();