using UnityEngine;

namespace BugFarmer.Entities
{
    /// <summary>
    /// Makes a fly wander around using Brownian motion.
    /// Attach to a fly sprite for autonomous buzzing movement.
    /// </summary>
    public class FlyBehavior : MonoBehaviour
    {
        [SerializeField] private float speed = 2f;
        [SerializeField] private float directionChangeInterval = 0.3f;
        [SerializeField] private float smoothing = 5f;
        [SerializeField] private float wanderRadius = 5f;

        private Vector2 _targetDirection;
        private Vector2 _currentDirection;
        private Vector2 _startPosition;
        private float _directionTimer;

        private void Start()
        {
            _startPosition = transform.position;
            PickNewDirection();
        }

        private void Update()
        {
            // Periodically pick a new random direction
            _directionTimer -= Time.deltaTime;
            if (_directionTimer <= 0f)
            {
                PickNewDirection();
                _directionTimer = directionChangeInterval + Random.Range(-0.1f, 0.1f);
            }

            // Smoothly interpolate toward target direction
            _currentDirection = Vector2.Lerp(_currentDirection, _targetDirection, smoothing * Time.deltaTime);

            // Move
            Vector2 newPos = (Vector2)transform.position + _currentDirection * speed * Time.deltaTime;

            // If too far from start, bias direction back toward center
            Vector2 toCenter = _startPosition - newPos;
            if (toCenter.magnitude > wanderRadius)
            {
                _targetDirection = toCenter.normalized;
            }

            transform.position = newPos;
        }

        private void PickNewDirection()
        {
            float angle = Random.Range(0f, 360f) * Mathf.Deg2Rad;
            _targetDirection = new Vector2(Mathf.Cos(angle), Mathf.Sin(angle));
        }

        /// <summary>
        /// Set the center point for wandering (called by spawner).
        /// </summary>
        public void SetHomePosition(Vector2 pos)
        {
            _startPosition = pos;
        }

        /// <summary>
        /// Property to get/set wander radius (for SwarmVisual to configure).
        /// </summary>
        public float WanderRadius
        {
            get => wanderRadius;
            set => wanderRadius = value;
        }
    }
}
